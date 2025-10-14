# app/api/v1/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Literal

from app.utils.s3_client import s3_client

router = APIRouter(prefix="/upload", tags=["Upload"])


class UploadResponse(BaseModel):
    """
    파일 업로드 응답
    
    Attributes:
        url: 업로드된 파일의 S3 URL
        filename: 원본 파일명
    """
    url: str
    filename: str


@router.post("", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(..., description="이미지 파일"),
    folder: Literal["images", "artworks", "exhibitions", "reactions"] = "images"
):
    """
    이미지 S3 업로드
    
    Args:
        file: 이미지 파일 (jpg, jpeg, png, gif, webp)
        folder: 저장 폴더 (images/artworks/exhibitions/reactions)
        
    Returns:
        UploadResponse: 업로드된 파일 URL
        
    Raises:
        400: 잘못된 파일 형식
        500: S3 업로드 실패
    """
    # 파일 확장자 확인
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # 파일 읽기
    file_content = await file.read()
    
    # S3 업로드
    s3_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_ext,
        folder=folder
    )
    
    if not s3_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to S3"
        )
    
    return UploadResponse(
        url=s3_url,
        filename=file.filename
    )


@router.post("/exhibition", response_model=UploadResponse)
async def upload_exhibition_poster(
    file: UploadFile = File(..., description="전시 포스터 이미지")
):
    """
    전시 포스터 업로드
    
    전용 엔드포인트로 자동으로 'exhibitions' 폴더에 저장
    """
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    file_content = await file.read()
    
    s3_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_ext,
        folder="exhibitions"
    )
    
    if not s3_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload exhibition poster"
        )
    
    return UploadResponse(url=s3_url, filename=file.filename)


@router.post("/artwork", response_model=UploadResponse)
async def upload_artwork_thumbnail(
    file: UploadFile = File(..., description="작품 썸네일 이미지")
):
    """
    작품 썸네일 업로드
    
    전용 엔드포인트로 자동으로 'artworks' 폴더에 저장
    """
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    file_content = await file.read()
    
    s3_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_ext,
        folder="artworks"
    )
    
    if not s3_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload artwork thumbnail"
        )
    
    return UploadResponse(url=s3_url, filename=file.filename)


@router.post("/reaction", response_model=UploadResponse)
async def upload_reaction_image(
    file: UploadFile = File(..., description="반응 이미지")
):
    """
    반응 이미지 업로드 (선택 사항)
    
    전용 엔드포인트로 자동으로 'reactions' 폴더에 저장
    """
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    file_content = await file.read()
    
    s3_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_ext,
        folder="reactions"
    )
    
    if not s3_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload reaction image"
        )
    
    return UploadResponse(url=s3_url, filename=file.filename)