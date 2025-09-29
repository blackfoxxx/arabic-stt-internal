"""
MinIO/S3 storage configuration and utilities
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, BinaryIO
from urllib.parse import urlparse
import minio
from minio import Minio
from minio.error import S3Error
import structlog
# import magic  # Commented out to avoid libmagic dependency
from io import BytesIO
import mimetypes

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global MinIO client
_minio_client: Optional[Minio] = None


async def init_minio() -> Minio:
    """Initialize MinIO client and create buckets"""
    global _minio_client
    
    try:
        _minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            region=settings.MINIO_REGION
        )
        
        # Create required buckets if they don't exist
        buckets = [
            settings.MEDIA_BUCKET,
            settings.PROCESSED_BUCKET,
            settings.EXPORTS_BUCKET,
            settings.MODELS_BUCKET
        ]
        
        for bucket_name in buckets:
            if not _minio_client.bucket_exists(bucket_name):
                _minio_client.make_bucket(bucket_name, location=settings.MINIO_REGION)
                logger.info("Created bucket", bucket=bucket_name)
            else:
                logger.debug("Bucket already exists", bucket=bucket_name)
        
        # Set bucket policies for public read on exports (for download links)
        exports_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{settings.EXPORTS_BUCKET}/*"
                }
            ]
        }
        
        try:
            import json
            _minio_client.set_bucket_policy(
                settings.EXPORTS_BUCKET, 
                json.dumps(exports_policy)
            )
        except S3Error as e:
            # Policy setting might fail in some MinIO configurations
            logger.warning("Failed to set bucket policy", bucket=settings.EXPORTS_BUCKET, error=str(e))
        
        logger.info("MinIO client initialized successfully")
        return _minio_client
        
    except Exception as e:
        logger.error("Failed to initialize MinIO client", error=str(e))
        raise


def get_minio() -> Minio:
    """Get MinIO client instance"""
    global _minio_client
    if not _minio_client:
        raise RuntimeError("MinIO client not initialized")
    return _minio_client


async def get_storage_health() -> bool:
    """Check storage health"""
    try:
        client = get_minio()
        # List buckets to test connectivity
        client.list_buckets()
        return True
    except Exception as e:
        logger.error("Storage health check failed", error=str(e))
        return False


class StorageManager:
    """Storage management utilities"""
    
    def __init__(self):
        self.client: Optional[Minio] = None
    
    def _get_client(self) -> Minio:
        """Get MinIO client"""
        if not self.client:
            self.client = get_minio()
        return self.client
    
    def generate_presigned_upload_url(
        self,
        bucket: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
        content_type: Optional[str] = None
    ) -> str:
        """Generate presigned URL for file upload"""
        try:
            client = self._get_client()
            
            # Add content type condition if specified
            conditions = {}
            if content_type:
                conditions["Content-Type"] = content_type
            
            url = client.presigned_put_object(
                bucket,
                object_name,
                expires=expires
            )
            
            return url
            
        except Exception as e:
            logger.error("Failed to generate presigned upload URL", 
                        bucket=bucket, object_name=object_name, error=str(e))
            raise
    
    def generate_presigned_download_url(
        self,
        bucket: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Generate presigned URL for file download"""
        try:
            client = self._get_client()
            url = client.presigned_get_object(
                bucket,
                object_name,
                expires=expires
            )
            return url
            
        except Exception as e:
            logger.error("Failed to generate presigned download URL",
                        bucket=bucket, object_name=object_name, error=str(e))
            raise
    
    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Upload file to storage"""
        try:
            client = self._get_client()
            
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Seek back to beginning
            
            # Upload file
            result = client.put_object(
                bucket,
                object_name,
                file_data,
                file_size,
                content_type=content_type,
                metadata=metadata
            )
            
            logger.info("File uploaded successfully",
                       bucket=bucket, object_name=object_name, 
                       size=file_size, etag=result.etag)
            return True
            
        except Exception as e:
            logger.error("Failed to upload file",
                        bucket=bucket, object_name=object_name, error=str(e))
            return False
    
    def download_file(self, bucket: str, object_name: str) -> Optional[bytes]:
        """Download file from storage"""
        try:
            client = self._get_client()
            response = client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
            
        except Exception as e:
            logger.error("Failed to download file",
                        bucket=bucket, object_name=object_name, error=str(e))
            return None
    
    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete file from storage"""
        try:
            client = self._get_client()
            client.remove_object(bucket, object_name)
            logger.info("File deleted successfully",
                       bucket=bucket, object_name=object_name)
            return True
            
        except Exception as e:
            logger.error("Failed to delete file",
                        bucket=bucket, object_name=object_name, error=str(e))
            return False
    
    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists"""
        try:
            client = self._get_client()
            client.stat_object(bucket, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error("Failed to check file existence",
                        bucket=bucket, object_name=object_name, error=str(e))
            return False
        except Exception as e:
            logger.error("Failed to check file existence",
                        bucket=bucket, object_name=object_name, error=str(e))
            return False
    
    def get_file_info(self, bucket: str, object_name: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            client = self._get_client()
            stat = client.stat_object(bucket, object_name)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "metadata": stat.metadata
            }
        except Exception as e:
            logger.error("Failed to get file info",
                        bucket=bucket, object_name=object_name, error=str(e))
            return None
    
    def list_files(
        self, 
        bucket: str, 
        prefix: str = "", 
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """List files in bucket"""
        try:
            client = self._get_client()
            objects = client.list_objects(
                bucket, 
                prefix=prefix, 
                recursive=True
            )
            
            files = []
            count = 0
            for obj in objects:
                if count >= max_keys:
                    break
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
                count += 1
            
            return files
            
        except Exception as e:
            logger.error("Failed to list files", bucket=bucket, prefix=prefix, error=str(e))
            return []
    
    def copy_file(
        self, 
        source_bucket: str, 
        source_object: str,
        dest_bucket: str, 
        dest_object: str
    ) -> bool:
        """Copy file between buckets/locations"""
        try:
            client = self._get_client()
            from minio.commonconfig import CopySource
            
            copy_source = CopySource(source_bucket, source_object)
            result = client.copy_object(dest_bucket, dest_object, copy_source)
            
            logger.info("File copied successfully",
                       source=f"{source_bucket}/{source_object}",
                       dest=f"{dest_bucket}/{dest_object}",
                       etag=result.etag)
            return True
            
        except Exception as e:
            logger.error("Failed to copy file",
                        source=f"{source_bucket}/{source_object}",
                        dest=f"{dest_bucket}/{dest_object}",
                        error=str(e))
            return False
    
    def generate_unique_object_name(self, prefix: str, extension: str) -> str:
        """Generate unique object name"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}/{timestamp}_{unique_id}.{extension.lstrip('.')}"


class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def validate_file_type(file_data: bytes, allowed_types: List[str]) -> tuple[bool, str]:
        """Validate file type using basic heuristics and file signatures"""
        try:
            # Basic file signature detection
            mime_type = "application/octet-stream"  # Default
            
            # Check common audio file signatures
            if file_data.startswith(b'\xff\xfb') or file_data.startswith(b'\xff\xf3') or file_data.startswith(b'\xff\xf2'):
                mime_type = "audio/mpeg"
            elif file_data.startswith(b'RIFF') and b'WAVE' in file_data[:12]:
                mime_type = "audio/wav"
            elif file_data.startswith(b'fLaC'):
                mime_type = "audio/flac"
            elif file_data.startswith(b'\x00\x00\x00\x20ftypM4A') or file_data.startswith(b'\x00\x00\x00\x18ftyp'):
                mime_type = "audio/mp4"
            elif file_data.startswith(b'OggS'):
                mime_type = "audio/ogg"
            # Add more file type detection as needed
            
            if mime_type in allowed_types or "audio/" in allowed_types:
                return True, mime_type
            else:
                return False, mime_type
                
        except Exception as e:
            logger.error("Failed to validate file type", error=str(e))
            return False, "unknown"
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str]:
        """Validate and sanitize filename"""
        # Remove path components and dangerous characters
        import re
        filename = os.path.basename(filename)
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Ensure filename is not empty and has reasonable length
        if not filename or len(filename) < 1:
            return False, "empty_filename"
        
        if len(filename) > 255:
            return False, "filename_too_long"
        
        # Ensure filename has extension
        if '.' not in filename:
            return False, "no_extension"
        
        return True, filename


# Global storage manager
storage = StorageManager()
file_validator = FileValidator()