import os
import mimetypes
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from boto3.s3.transfer import TransferConfig

logger = logging.getLogger(__name__)

def get_s3_client() -> boto3.client:
    """
    Initializes and returns an S3-compatible client using environment variables.
    Supports standard AWS S3 and any S3-compatible services (MinIO, R2, Wasabi, etc.)
    by utilizing the S3_ENDPOINT_URL variable.
    """
    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region_name = os.getenv("AWS_REGION", "us-east-1")
    
    # Custom configuration for robust uploads
    config = Config(
        retries={"max_attempts": 3, "mode": "standard"},
        signature_version="s3v4",
        s3={
            'chunked_encoding_enabled': False,
            'payload_signing_enabled': False,
            'request_checksum_calculation': 'when_required',
            'response_checksum_validation': 'when_required'
        }
    )

    client_kwargs = {
        "service_name": "s3",
        "region_name": region_name,
        "config": config
    }

    # If using an S3-compatible provider, specify the custom endpoint URL
    if endpoint_url:
        client_kwargs["endpoint_url"] = endpoint_url

    # Credentials will automatically fall back to standard AWS credential provider chain if not set
    if aws_access_key and aws_secret_key:
        client_kwargs["aws_access_key_id"] = aws_access_key
        client_kwargs["aws_secret_access_key"] = aws_secret_key

    return boto3.client(**client_kwargs)


def upload_video_to_s3(
    local_file_path: str,
    s3_key: Optional[str] = None,
    bucket_name: Optional[str] = None,
    generate_presigned: bool = False,
    presigned_expiry_seconds: int = 3600
) -> str:
    """
    Uploads a video file from local disk to S3/S3-compatible object storage.

    Args:
        local_file_path (str): Path to the video file on the local disk.
        s3_key (Optional[str]): S3 object key (path inside bucket). Defaults to file basename.
        bucket_name (Optional[str]): Target S3 bucket name. Defaults to S3_BUCKET_NAME env var.
        generate_presigned (bool): If True, returns a temporary pre-signed URL. 
                                  If False, returns the public URL.
        presigned_expiry_seconds (int): Expiry time for pre-signed URL (default: 1 hour).

    Returns:
        str: Public or Pre-signed URL of the uploaded video.
    """
    # 1. Validate inputs and environment config
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local video file not found at: {local_file_path}")

    bucket = bucket_name or os.getenv("S3_BUCKET_NAME")
    if not bucket:
        raise ValueError("Target bucket name must be provided or configured via 'S3_BUCKET_NAME' env var.")

    if not s3_key:
        s3_key = os.path.basename(local_file_path)

    # Automatically detect MIME type for streaming compatibility
    content_type, _ = mimetypes.guess_type(local_file_path)
    if not content_type:
        content_type = "video/mp4"

    s3_client = get_s3_client()

    # 2. Upload file
    logger.info(f"Uploading '{local_file_path}' to bucket '{bucket}' with key '{s3_key}'...")
    try:
        extra_args = {}
        # If returning a public URL and not using pre-signed links, set ACL to public-read if permitted
        # Note: Some providers (like Cloudflare R2) do not support ACLs, or they may be disabled on AWS.
        use_public_acl = os.getenv("S3_USE_PUBLIC_ACL", "false").lower() == "true"
        if use_public_acl and not generate_presigned:
            extra_args["ACL"] = "public-read"

        with open(local_file_path, "rb") as f:
            file_data = f.read()

        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type,
            **extra_args
        )
        logger.info("Upload completed successfully.")

    except ClientError as e:
        logger.error(f"S3 Upload failed: {e}")
        raise e

    # 3. Generate and return URL
    if generate_presigned:
        try:
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": s3_key},
                ExpiresIn=presigned_expiry_seconds
            )
            return presigned_url
        except ClientError as e:
            logger.error(f"Failed to generate pre-signed URL: {e}")
            raise e
    else:
        # Construct standard public S3 or custom endpoint URL
        endpoint_url = os.getenv("S3_ENDPOINT_URL")
        if endpoint_url:
            # e.g., https://my-custom-endpoint.com/bucket/key or https://bucket.my-custom-endpoint.com/key
            endpoint_url = endpoint_url.rstrip("/")
            # Standard path-style address for compatibility
            return f"{endpoint_url}/{bucket}/{s3_key}"
        else:
            region = os.getenv("AWS_REGION", "us-east-1")
            return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
