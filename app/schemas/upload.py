"""
Upload Schemas
"""
from pydantic import BaseModel, Field


# ============================================================================
# Response Schemas
# ============================================================================

class UploadResponse(BaseModel):
    """파일 업로드 응답"""
    url: str = Field(..., description="업로드된 파일의 S3 URL")
    filename: str = Field(..., description="원본 파일명")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://axxxxxx.xxx.com",
                "filename": "artwork_photo.jpg",
            }
        }


class DeleteImageResponse(BaseModel):
    """이미지 삭제 응답"""
    success: bool = Field(..., description="삭제 성공 여부")
    message: str = Field(..., description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "이미지가 성공적으로 삭제되었습니다.",
            }
        }