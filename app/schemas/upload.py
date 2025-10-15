from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """
    파일 업로드 응답
    
    Attributes:
        url: 업로드된 파일의 S3 URL
        filename: 원본 파일명
    """
    url: str = Field(..., description="업로드된 파일의 S3 URL")
    filename: str = Field(..., description="원본 파일명")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/abc123.jpg",
                "filename": "artwork_photo.jpg"
            }
        }


class DeleteImageResponse(BaseModel):
    """
    이미지 삭제 응답
    
    Attributes:
        success: 삭제 성공 여부
        message: 결과 메시지
    """
    success: bool = Field(..., description="삭제 성공 여부")
    message: str = Field(..., description="결과 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "이미지가 성공적으로 삭제되었습니다."
            }
        }