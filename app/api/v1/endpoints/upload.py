import logging

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.schemas.upload import DeleteImageResponse, UploadResponse
from app.utils.s3_client import s3_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])

# 허용되는 이미지 확장자
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def validate_image(file: UploadFile) -> str:
    """
    이미지 파일 검증

    Args:
        file: 업로드된 파일

    Returns:
        파일 확장자

    Raises:
        HTTPException: 유효하지 않은 파일
    """
    # 파일 확장자 추출
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="파일명이 없습니다")

    extension = file.filename.split(".")[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    return extension


@router.post(
    "",
    response_model=UploadResponse,
    summary="이미지 업로드",
    description="""
    이미지 S3 업로드

    Args:
        file: 이미지 파일 (jpg, jpeg, png, gif, webp)
        folder: 저장 폴더 (images/artworks/exhibitions/reactions)

    Returns:
        UploadResponse: 업로드된 파일 URL

    Raises:
        400: 잘못된 파일 형식
        500: S3 업로드 실패
    """,
)
async def upload_image(
    file: UploadFile = File(..., description="이미지 파일"),
    folder: str = Query(
        default="images", enum=["images", "artworks", "exhibitions", "reactions"]
    ),
):
    """일반 이미지 업로드"""
    try:
        # 파일 검증
        validate_image(file)

        # S3 업로드
        file_url = await s3_client.upload_file(file=file, folder=folder)

        return UploadResponse(url=file_url, filename=file.filename or "unknown")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"업로드 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="파일 업로드 중 오류가 발생했습니다"
        )


@router.post(
    "/exhibition",
    response_model=UploadResponse,
    summary="전시 포스터 업로드",
    description="""
    전시 포스터 업로드

    전용 엔드포인트로 자동으로 'exhibitions' 폴더에 저장
    """,
)
async def upload_exhibition_poster(
    file: UploadFile = File(..., description="전시 포스터 이미지")
):
    """전시 포스터 업로드 (exhibitions 폴더)"""
    try:
        # 파일 검증
        validate_image(file)

        # S3 업로드
        file_url = await s3_client.upload_file(file=file, folder="exhibitions")

        return UploadResponse(url=file_url, filename=file.filename or "unknown")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"전시 포스터 업로드 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="파일 업로드 중 오류가 발생했습니다"
        )


@router.post(
    "/artwork",
    response_model=UploadResponse,
    summary="작품 썸네일 업로드",
    description="""
    작품 썸네일 업로드

    전용 엔드포인트로 자동으로 'artworks' 폴더에 저장
    """,
)
async def upload_artwork_thumbnail(
    file: UploadFile = File(..., description="작품 썸네일 이미지")
):
    """작품 썸네일 업로드 (artworks 폴더)"""
    try:
        # 파일 검증
        validate_image(file)

        # S3 업로드
        file_url = await s3_client.upload_file(file=file, folder="artworks")

        return UploadResponse(url=file_url, filename=file.filename or "unknown")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"작품 썸네일 업로드 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="파일 업로드 중 오류가 발생했습니다"
        )


@router.post(
    "/reaction",
    response_model=UploadResponse,
    summary="반응 이미지 업로드",
    description="""
    반응 이미지 업로드 (선택 사항)

    전용 엔드포인트로 자동으로 'reactions' 폴더에 저장
    """,
)
async def upload_reaction_image(
    file: UploadFile = File(..., description="반응 이미지")
):
    """반응 이미지 업로드 (reactions 폴더)"""
    try:
        # 파일 검증
        validate_image(file)

        # S3 업로드
        file_url = await s3_client.upload_file(file=file, folder="reactions")

        return UploadResponse(url=file_url, filename=file.filename or "unknown")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"반응 이미지 업로드 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="파일 업로드 중 오류가 발생했습니다"
        )


@router.delete(
    "",
    response_model=DeleteImageResponse,
    summary="이미지 삭제",
    description="""
    S3에서 이미지 삭제

    사용 케이스:
    - Reaction 저장 전 취소 시
    - 잘못 업로드한 이미지 정리
    - 임시 업로드 파일 삭제

    Args:
        url: 삭제할 S3 이미지 URL (Query Parameter)

    Returns:
        DeleteImageResponse: 삭제 성공 여부

    Example:
        DELETE /api/v1/upload?url=https://bucket.s3.region.amazonaws.com/reactions/abc.jpg
    """,
)
async def delete_image(url: str = Query(..., description="삭제할 S3 이미지 URL")):
    """
    S3 이미지 삭제

    Reaction 저장 전 취소하거나 잘못 업로드한 이미지를 삭제할 때 사용
    """
    try:
        success = s3_client.delete_file(url)

        if success:
            return DeleteImageResponse(
                success=True, message="이미지가 성공적으로 삭제되었습니다."
            )
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="이미지 삭제에 실패했습니다.")

    except Exception as e:
        logger.error(f"이미지 삭제 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 삭제 중 오류가 발생했습니다: {str(e)}"
        )