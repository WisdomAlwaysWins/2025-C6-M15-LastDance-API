import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 클라이언트"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_file(
        self,
        file_content: bytes,
        file_extension: str,
        folder: str = "images"
    ) -> Optional[str]:
        """
        S3에 파일 업로드
        
        Args:
            file_content: 파일 바이트 데이터
            file_extension: 파일 확장자 (예: 'jpg', 'png')
            folder: S3 내 폴더 경로 (예: 'artworks', 'reviews')
        
        Returns:
            업로드된 파일의 S3 URL 또는 None (실패 시)
        """
        try:
            # 고유한 파일명 생성
            file_name = f"{folder}/{uuid.uuid4()}.{file_extension}"
            
            # S3에 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_content,
                ContentType=f"image/{file_extension}"
            )
            
            # 업로드된 파일의 URL 생성
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"
            
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return None
    
    def delete_file(self, file_url: str) -> bool:
        """
        S3에서 파일 삭제
        
        Args:
            file_url: 삭제할 파일의 S3 URL
        
        Returns:
            성공 여부
        """
        try:
            # URL에서 파일 키 추출
            # 예: https://bucket.s3.region.amazonaws.com/folder/file.jpg -> folder/file.jpg
            file_key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[1]
            
            # S3에서 삭제
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            logger.info(f"File deleted successfully: {file_url}")
            return True
            
        except (ClientError, IndexError) as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
    
    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        임시 접근 URL 생성 (Presigned URL)
        
        Args:
            file_key: S3 파일 키
            expiration: URL 유효 시간 (초)
        
        Returns:
            Presigned URL 또는 None
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None


# 싱글톤 인스턴스
s3_client = S3Client()