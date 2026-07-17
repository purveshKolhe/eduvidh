import os
import json
import uuid
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

NUMBER_SCALE = Decimal("0.001")
NUMBER_MAX = Decimal("9999999.999")  # NUMBER(10, 3)


def _number(value: Any) -> Decimal:
    """Return a value Oracle can store exactly in NUMBER(10, 3)."""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("metric must be a finite decimal") from error
    if not number.is_finite():
        raise ValueError("metric must be a finite decimal")
    number = number.quantize(NUMBER_SCALE, rounding=ROUND_HALF_UP)
    if abs(number) > NUMBER_MAX:
        raise ValueError("metric exceeds Oracle NUMBER(10, 3) range")
    return number


def _json_clob(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _video_id(value: str) -> str:
    if not isinstance(value, str) or len(value) != 36:
        raise ValueError("video_id must be a UUID string fitting VARCHAR2(36)")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as error:
        raise ValueError("video_id must be a UUID string fitting VARCHAR2(36)") from error
    if str(parsed) != value.lower():
        raise ValueError("video_id must use the canonical UUID format")
    return value


class BaseAdapter:
    def create_video(self, prompt: str) -> str:
        raise NotImplementedError()

    def update_video(
        self,
        video_id: str,
        status: Optional[str] = None,
        slides_data: Optional[list] = None,
        video_storage_url: Optional[str] = None,
        error_message: Optional[str] = None,
        cold_start_time: Optional[float] = None,
        rendering_time: Optional[float] = None,
        video_length: Optional[float] = None,
        resources_used: Optional[dict] = None
    ) -> None:
        raise NotImplementedError()

    def get_video(self, video_id: str) -> Dict[str, Any]:
        raise NotImplementedError()

    def upload_video(self, local_file_path: str, video_id: str) -> str:
        raise NotImplementedError()


# ============================================================================
# ORACLE & S3 ADAPTER
# ============================================================================
class OracleS3Adapter(BaseAdapter):
    def __init__(self):
        import oracledb
        self.oracledb = oracledb
        
        # Oracle Configuration
        self.db_user = os.getenv("ORACLE_DB_USER") or os.getenv("DB_USER", "ADMIN")
        self.db_password = os.getenv("ORACLE_DB_PASSWORD") or os.getenv("DB_PASSWORD")
        self.db_dsn = os.getenv("ORACLE_DB_DSN") or os.getenv("videopipeline_tp")
        
        if not self.db_password or not self.db_dsn:
            raise ValueError("Oracle credentials (DB_PASSWORD / videopipeline_tp) must be set in env.")

        # S3 Configuration
        from db_and_storage.s3_helper import upload_video_to_s3
        self.upload_video_fn = upload_video_to_s3

    def _get_connection(self):
        # Establish thin connection to Oracle DB
        return self.oracledb.connect(
            user=self.db_user,
            password=self.db_password,
            dsn=self.db_dsn
        )

    def create_video(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        video_id = str(uuid.uuid4())
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                # Insert statement with columns matching Oracle schema
                sql = """
                    INSERT INTO videos (id, prompt, status, created_at, updated_at)
                    VALUES (:id, :prompt, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                cursor.setinputsizes(prompt=self.oracledb.DB_TYPE_CLOB)
                cursor.execute(sql, {"id": video_id, "prompt": prompt, "status": "pending"})
            connection.commit()
            return video_id
        finally:
            connection.close()

    def update_video(
        self,
        video_id: str,
        status: Optional[str] = None,
        slides_data: Optional[list] = None,
        video_storage_url: Optional[str] = None,
        error_message: Optional[str] = None,
        cold_start_time: Optional[float] = None,
        rendering_time: Optional[float] = None,
        video_length: Optional[float] = None,
        resources_used: Optional[dict] = None
    ) -> None:
        video_id = _video_id(video_id)
        connection = self._get_connection()
        try:
            updates = []
            params = {}
            
            if status is not None:
                if not isinstance(status, str) or len(status) > 50:
                    raise ValueError("status exceeds VARCHAR2(50)")
                updates.append("status = :status")
                params["status"] = status
            if slides_data is not None:
                updates.append("slides_data = :slides_data")
                params["slides_data"] = _json_clob(slides_data)
            if video_storage_url is not None:
                if not isinstance(video_storage_url, str) or len(video_storage_url) > 2048:
                    raise ValueError("video_storage_url exceeds VARCHAR2(2048)")
                updates.append("video_storage_url = :video_storage_url")
                params["video_storage_url"] = video_storage_url
            if error_message is not None:
                if not isinstance(error_message, str):
                    raise ValueError("error_message must be a CLOB string")
                updates.append("error_message = :error_message")
                params["error_message"] = error_message
            if cold_start_time is not None:
                updates.append("cold_start_time = :cold_start_time")
                params["cold_start_time"] = _number(cold_start_time)
            if rendering_time is not None:
                updates.append("rendering_time = :rendering_time")
                params["rendering_time"] = _number(rendering_time)
            if video_length is not None:
                updates.append("video_length = :video_length")
                params["video_length"] = _number(video_length)
            if resources_used is not None:
                updates.append("resources_used = :resources_used")
                params["resources_used"] = _json_clob(resources_used)

            if updates:
                sql = f"UPDATE videos SET {', '.join(updates)} WHERE id = :video_id"
                params["video_id"] = video_id
                with connection.cursor() as cursor:
                    clob_binds = {
                        name: self.oracledb.DB_TYPE_CLOB
                        for name in ("slides_data", "error_message", "resources_used")
                        if name in params
                    }
                    if clob_binds:
                        cursor.setinputsizes(**clob_binds)
                    cursor.execute(sql, params)
                    if cursor.rowcount != 1:
                        raise LookupError(f"video not found: {video_id}")
                connection.commit()
        finally:
            connection.close()

    def get_video(self, video_id: str) -> Dict[str, Any]:
        video_id = _video_id(video_id)
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT id, prompt, status, slides_data, video_storage_url, error_message, 
                           cold_start_time, rendering_time, video_length, resources_used, created_at, updated_at
                    FROM videos WHERE id = :1
                """
                cursor.execute(sql, (video_id,))
                row = cursor.fetchone()
                if not row:
                    return {}

                # Helper to read LOB values (CLOBs require reading in cx_Oracle/oracledb)
                def read_lob(val):
                    if hasattr(val, "read"):
                        return val.read()
                    return val

                slides_data_raw = read_lob(row[3])
                resources_used_raw = read_lob(row[9])

                return {
                    "id": row[0],
                    "prompt": read_lob(row[1]),
                    "status": row[2],
                    "slides_data": json.loads(slides_data_raw) if slides_data_raw else None,
                    "video_storage_url": row[4],
                    "error_message": read_lob(row[5]),
                    "cold_start_time": row[6],
                    "rendering_time": row[7],
                    "video_length": row[8],
                    "resources_used": json.loads(resources_used_raw) if resources_used_raw else None,
                    "created_at": row[10].isoformat() if row[10] else None,
                    "updated_at": row[11].isoformat() if row[11] else None,
                }
        finally:
            connection.close()

    def upload_video(self, local_file_path: str, video_id: str) -> str:
        video_id = _video_id(video_id)
        s3_key = f"videos/{video_id}/final.mp4"
        return self.upload_video_fn(
            local_file_path=local_file_path,
            s3_key=s3_key
        )


# ============================================================================
# FACTORY FUNCTION
# ============================================================================
def get_adapter() -> BaseAdapter:
    """Returns the configured Oracle and S3 backend adapter."""
    return OracleS3Adapter()
