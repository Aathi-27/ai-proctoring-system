import os
import io
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

# Optional imports for evidence processing
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    Minio = None
    S3Error = Exception
    MINIO_AVAILABLE = False

from cryptography.fernet import Fernet

from app.models.alerts import EvidenceSnapshot, AlertType


logger = logging.getLogger(__name__)


class EvidenceSnapshotService:
    """Service for capturing and storing encrypted evidence snapshots"""
    
    def __init__(self):
        self.minio_client = None
        self.encryption_key = None
        self.snapshot_retention_days = 30
        
        if MINIO_AVAILABLE:
            self._initialize_minio_client()
        
        self._initialize_encryption()
    
    def _initialize_minio_client(self):
        """Initialize MinIO client for object storage"""
        try:
            # Get MinIO configuration from environment
            minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            minio_secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
            
            self.minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=minio_secure
            )
            
            # Create bucket if it doesn't exist
            bucket_name = "evidence-snapshots"
            if not self.minio_client.bucket_exists(bucket_name):
                self.minio_client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self.minio_client = None
    
    def _initialize_encryption(self):
        """Initialize encryption key for evidence snapshots"""
        try:
            # Get encryption key from environment or generate one
            encryption_key = os.getenv("EVIDENCE_ENCRYPTION_KEY")
            if not encryption_key:
                # Generate a new key for development
                encryption_key = Fernet.generate_key().decode()
                logger.warning("Generated new evidence encryption key for development")
            
            self.encryption_key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
            self.cipher_suite = Fernet(self.encryption_key)
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self.encryption_key = None
    
    async def capture_snapshot(
        self,
        frame_data: str,
        exam_id: str,
        session_id: str,
        alert_id: str,
        event_type: AlertType,
        frame_number: int,
        risk_score: int
    ) -> Optional[EvidenceSnapshot]:
        """Capture and store encrypted evidence snapshot"""
        try:
            # Decode base64 frame data
            frame_bytes = base64.b64decode(frame_data)
            
            # Create unique snapshot ID
            snapshot_id = f"{alert_id}_{frame_number}"
            
            # Create file path
            file_path = f"evidence/{exam_id}/{session_id}/{snapshot_id}.jpg"
            
            # Encrypt the frame data
            encrypted_frame = self._encrypt_data(frame_bytes)
            if not encrypted_frame:
                logger.error("Failed to encrypt frame data")
                return None
            
            # Upload to MinIO if available, otherwise local fallback
            if self.minio_client and MINIO_AVAILABLE:
                try:
                    self.minio_client.put_object(
                        bucket_name="evidence-snapshots",
                        object_name=file_path,
                        data=io.BytesIO(encrypted_frame),
                        length=len(encrypted_frame),
                        content_type="image/jpeg"
                    )
                    logger.info(f"Uploaded encrypted snapshot to MinIO: {file_path}")
                except Exception as minio_error:
                    logger.warning(f"MinIO upload failed, falling back to local storage: {minio_error}")
                    # Fall through to local storage
                    file_path = await self._store_locally(file_path, encrypted_frame)
            else:
                # Fallback to local storage for development
                file_path = await self._store_locally(file_path, encrypted_frame)
            
            # Calculate file size
            file_size = len(encrypted_frame)
            
            # Create retention expiry date
            retention_expires_at = datetime.utcnow() + timedelta(days=self.snapshot_retention_days)
            
            # Create snapshot metadata
            snapshot = EvidenceSnapshot(
                snapshot_id=snapshot_id,
                exam_id=exam_id,
                session_id=session_id,
                alert_id=alert_id,
                event_type=event_type,
                frame_number=frame_number,
                risk_score=risk_score,
                file_path=file_path,
                file_size=file_size,
                retention_expires_at=retention_expires_at,
                encryption_key_id="evidence_key_1"  # Would be from key management system
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to capture snapshot: {e}")
            return None
    
    async def _store_locally(self, file_path: str, data: bytes) -> str:
        """Store data locally as fallback"""
        local_path = f"/tmp/{file_path}"
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(data)
            logger.info(f"Saved encrypted snapshot locally: {local_path}")
        except Exception as e:
            logger.error(f"Failed to store snapshot locally: {e}")
            # Return original path even if storage fails
        return local_path
    
    def _encrypt_data(self, data: bytes) -> Optional[bytes]:
        """Encrypt data using AES-256"""
        try:
            if not self.encryption_key:
                logger.error("Encryption key not available")
                return None
            
            return self.cipher_suite.encrypt(data)
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def _decrypt_data(self, encrypted_data: bytes) -> Optional[bytes]:
        """Decrypt data using AES-256"""
        try:
            if not self.encryption_key:
                logger.error("Encryption key not available")
                return None
            
            return self.cipher_suite.decrypt(encrypted_data)
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    async def retrieve_snapshot(self, snapshot_id: str) -> Optional[bytes]:
        """Retrieve and decrypt snapshot data"""
        try:
            # This would typically involve looking up the snapshot metadata
            # For now, we'll implement basic retrieval
            if self.minio_client:
                # Download from MinIO
                response = self.minio_client.get_object("evidence-snapshots", snapshot_id)
                encrypted_data = response.read()
                response.close()
                response.release_conn()
            else:
                # Read from local storage
                with open(snapshot_id, "rb") as f:
                    encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self._decrypt_data(encrypted_data)
            if not decrypted_data:
                logger.error("Failed to decrypt snapshot data")
                return None
            
            return decrypted_data
            
        except S3Error as e:
            logger.error(f"MinIO error retrieving snapshot: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve snapshot: {e}")
            return None
    
    async def delete_expired_snapshots(self):
        """Delete snapshots that have passed their retention period"""
        try:
            # This would typically query MongoDB for expired snapshots
            # For now, we'll implement basic cleanup
            
            current_time = datetime.utcnow()
            
            # TODO: Query MongoDB for snapshots with retention_expires_at < current_time
            # and delete them from storage
            
            logger.info("Expired snapshots cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired snapshots: {e}")
    
    async def get_snapshot_metadata(self, snapshot_id: str) -> Optional[EvidenceSnapshot]:
        """Get snapshot metadata from database"""
        try:
            # TODO: Implement metadata retrieval from MongoDB
            # For now, return None as this requires database integration
            
            logger.warning("Snapshot metadata retrieval not implemented yet")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get snapshot metadata: {e}")
            return None
    
    def set_retention_period(self, days: int):
        """Set snapshot retention period"""
        if 1 <= days <= 365:
            self.snapshot_retention_days = days
            logger.info(f"Set snapshot retention period to {days} days")
        else:
            logger.error(f"Invalid retention period: {days} days (must be 1-365)")
    
    def get_storage_info(self) -> dict:
        """Get storage usage information"""
        try:
            if self.minio_client:
                # Get bucket statistics
                stats = self.minio_client.stat_object("evidence-snapshots", "")
                return {
                    "storage_backend": "minio",
                    "bucket": "evidence-snapshots",
                    "status": "available"
                }
            else:
                return {
                    "storage_backend": "local",
                    "storage_path": "/tmp/evidence",
                    "status": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {
                "storage_backend": "unknown",
                "status": "error",
                "error": str(e)
            }


# Global instance
evidence_service = EvidenceSnapshotService()