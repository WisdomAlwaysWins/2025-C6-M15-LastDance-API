from app.config import settings
from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> bool:
    """
    Admin API Key 검증

    Args:
        x_api_key: Header의 X-API-Key 값

    Returns:
        bool: 검증 성공

    Raises:
        HTTPException: API Key가 유효하지 않음
    """
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 API Key입니다",
        )
    return True
