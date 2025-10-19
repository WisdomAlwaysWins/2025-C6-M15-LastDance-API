import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
import time
import os
from fastapi import UploadFile
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
    
    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
        exhibition_id: int = None,
        visitor_id: int = None
    ) -> str:
        """
        S3에 파일 업로드
        
        Args:
            file: 업로드할 파일
            folder: 폴더 (reactions, artworks 등)
            exhibition_id: 전시 ID
            visitor_id: 관람객 ID
        
        Returns:
            str: S3 파일 URL
        """
        try:
            # 파일 읽기
            contents = await file.read()
            
            # 환경 (production or test)
            env = os.getenv("ENVIRONMENT", "production")
            
            # 파일명 생성
            timestamp = int(time.time())
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_id = str(uuid.uuid4())[:8]
            
            # reactions 폴더 구조
            if folder == "reactions" and exhibition_id and visitor_id:
                s3_key = f"{folder}/{env}/exhibition_{exhibition_id}/visitor_{visitor_id}_{timestamp}_{unique_id}.{file_extension}"
            else:
                # 기존 방식
                filename = f"{uuid.uuid4()}.{file_extension}"
                s3_key = f"{folder}/{filename}"
            
            # S3 업로드
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=contents,
                ContentType=file.content_type or 'image/jpeg'
            )
            
            # URL 생성
            file_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"✅ S3 업로드 성공: {s3_key}")
            return file_url
            
        except Exception as e:
            logger.error(f"❌ S3 업로드 실패: {e}")
            raise
    
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