# Database and Object Storage Modules

This module contains clean database migration scripts, data schema representations (using SQLAlchemy and Pydantic), and a flexible S3-compatible object storage file upload helper.

## Files Created

1. **[migration.sql](file:///home/purvi/Desktop/eduvidh/db_and_storage/migration.sql)**: Relational Database migration script targeting PostgreSQL (default) and MySQL (commented fallback).
2. **[schema.py](file:///home/purvi/Desktop/eduvidh/db_and_storage/schema.py)**: SQLAlchemy ORM model and Pydantic schema models to represent, validate, and serialize video metadata.
3. **[s3_helper.py](file:///home/purvi/Desktop/eduvidh/db_and_storage/s3_helper.py)**: File upload helper function utilizing `boto3` to upload local video files to S3/S3-compatible object stores.

---

## Configuration

All connections and settings are driven by environment variables. Below are the key environment variables used:

### S3 / Object Storage configuration
* `S3_BUCKET_NAME`: The target bucket name for uploads.
* `S3_ENDPOINT_URL`: (Optional) Custom URL for S3-compatible providers (e.g. MinIO, Cloudflare R2, DigitalOcean Spaces, Wasabi). If omitted, standard AWS S3 URLs are generated.
* `AWS_ACCESS_KEY_ID`: S3/AWS Access Key ID.
* `AWS_SECRET_ACCESS_KEY`: S3/AWS Secret Access Key.
* `AWS_REGION`: Target region (default: `us-east-1`).
* `S3_USE_PUBLIC_ACL`: Set to `true` to apply `public-read` ACLs during upload (only if supported by the provider).

---

## Usage Example

### 1. Database Connection and ORM (SQLAlchemy)
```python
from sqlalchemy import create_client, create_engine
from sqlalchemy.orm import sessionmaker
from db_and_storage.schema import VideoORM

# Example Database engine initialization
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Insert metadata into the database
db = SessionLocal()
db_video = VideoORM(
    prompt="A futuristic city with high speed trains",
    cold_start_time=1.240,
    rendering_time=12.450,
    video_length=15.000,
    resources_used={"max_ram_usage_mb": 512, "peak_cpu_percent": 87.5},
    video_storage_url="https://my-bucket.s3.amazonaws.com/rendered_video.mp4"
)
db.add(db_video)
db.commit()
db.refresh(db_video)
print(db_video.to_dict())
```

### 2. S3 Video Upload
```python
from db_and_storage.s3_helper import upload_video_to_s3

# Standard upload yielding a public URL
public_url = upload_video_to_s3(
    local_file_path="/tmp/video.mp4",
    s3_key="renders/my-amazing-video.mp4"
)
print("Public URL:", public_url)

# Upload yielding a secure, temporary pre-signed URL (expiring in 1 hour)
secure_url = upload_video_to_s3(
    local_file_path="/tmp/video.mp4",
    s3_key="renders/my-secure-video.mp4",
    generate_presigned=True,
    presigned_expiry_seconds=3600
)
print("Secure Pre-signed URL:", secure_url)
```
