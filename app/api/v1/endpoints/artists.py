from datetime import datetime
from typing import List
import uuid as uuid_lib

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Header

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import (
    ArtistCreate, 
    ArtistResponse, 
    ArtistUpdate,
    ArtistLoginRequest,  
    ArtistLoginResponse,  
)
from app.utils.code_generator import generate_login_code  
from app.config import settings

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get(
    "",
    response_model=List[ArtistResponse],
    summary="작가 목록 조회",
    description="작가 목록을 조회합니다.",
)
def get_artists(db: Session = Depends(get_db)):
    """
    작가 전체 조회

    Returns:
        List[ArtistResponse]: 작가 목록
    """
    artists = db.query(Artist).order_by(Artist.id).all()
    return artists


@router.get(
    "/{artist_id}",
    response_model=ArtistResponse,
    summary="작가 상세 조회",
    description="작가 ID로 상세 정보를 조회합니다.",
)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    """
    작가 상세 조회

    Args:
        artist_id: 작가 ID

    Returns:
        ArtistResponse: 작가 정보

    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found",
        )
    return artist


@router.get("/uuid/{uuid}", response_model=ArtistResponse)
def get_artist_by_uuid(uuid: str, db: Session = Depends(get_db)):
    """
    작가 UUID로 조회

    Args:
        uuid: 작가 UUID

    Returns:
        ArtistResponse: 작가 정보

    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.uuid == uuid).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with uuid {uuid} not found",
        )
    return artist


@router.post(
    "",
    response_model=ArtistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="작가 생성",
    description="새 작가를 등록합니다. 로그인 코드 자동 생성. (관리자 전용, API Key 필요)",
)
def create_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),  
):
    """
    작가 생성 (관리자)

    Args:
        artist_data: 작가 생성 데이터
        x_api_key: 관리자 API Key

    Returns:
        ArtistResponse: 생성된 작가 정보 (login_code 포함)

    Note:
        - UUID 자동 생성
        - login_code 자동 생성 (6자리)
    """
    # Admin 인증
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    # UUID 생성
    artist_uuid = str(uuid_lib.uuid4())
    
    # 로그인 코드 생성
    login_code = generate_login_code()
    
    # 중복 확인 (매우 낮은 확률이지만)
    while db.query(Artist).filter(Artist.login_code == login_code).first():
        login_code = generate_login_code()
    
    # 작가 생성
    new_artist = Artist(
        uuid=artist_uuid,
        name=artist_data.name,
        bio=artist_data.bio,
        email=artist_data.email,
        login_code=login_code,  
        login_code_created_at=datetime.now(),  
    )
    
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist


# 작가 로그인
@router.post(
    "/login",
    response_model=ArtistLoginResponse,
    summary="작가 로그인",
    description="6자리 로그인 코드로 작가 인증",
)
def login_artist(
    request: ArtistLoginRequest,
    db: Session = Depends(get_db),
):
    """
    작가 로그인

    Args:
        request: 로그인 코드

    Returns:
        ArtistLoginResponse: 작가 정보

    Raises:
        404: 유효하지 않은 로그인 코드
    """
    artist = db.query(Artist).filter(
        Artist.login_code == request.login_code
    ).first()
    
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 로그인 코드입니다"
        )
    
    return artist


@router.put(
    "/{artist_id}",
    response_model=ArtistResponse,
    summary="작가 수정",
    description="작가 정보를 수정합니다. (관리자 전용, API Key 필요)",
)
def update_artist(
    artist_id: int, 
    artist_data: ArtistUpdate, 
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),  # NEW
):
    """
    작가 정보 수정 (관리자)

    Args:
        artist_id: 작가 ID
        artist_data: 수정 데이터
        x_api_key: 관리자 API Key

    Returns:
        ArtistResponse: 수정된 작가 정보

    Raises:
        404: 작가를 찾을 수 없음
    """
    # Admin 인증
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artist with id {artist_id} not found",
        )

    update_data = artist_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(artist, key, value)

    db.commit()
    db.refresh(artist)
    return artist


@router.delete(
    "/{artist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="작가 삭제",
    description="작가를 삭제합니다. (관리자 전용, API Key 필요)",
)
def delete_artist(
    artist_id: int, 
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),  # NEW
):
    """
    작가 삭제 (관리자)

    Args:
        artist_id: 작가 ID
        x_api_key: 관리자 API Key

    Raises:
        404: 작가를 찾을 수 없음
    """
    # Admin 인증
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
        )

    db.delete(artist)
    db.commit()
    return None


# 개별 작가 코드 재생성
@router.post(
    "/{artist_id}/regenerate-login-code",
    response_model=ArtistResponse,
    summary="작가 로그인 코드 재생성",
    description="기존 작가의 로그인 코드를 재생성합니다. (관리자 전용)",
)
def regenerate_artist_login_code(
    artist_id: int,
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """
    작가 로그인 코드 재생성 (관리자)

    Args:
        artist_id: 작가 ID
        x_api_key: 관리자 API Key

    Returns:
        ArtistResponse: 새로운 login_code가 포함된 작가 정보

    Raises:
        403: 권한 없음
        404: 작가를 찾을 수 없음
    """
    # Admin 인증
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artist_id}를 찾을 수 없습니다"
        )
    
    # 새 코드 생성
    new_code = generate_login_code()
    
    # 중복 확인
    while db.query(Artist).filter(Artist.login_code == new_code).first():
        new_code = generate_login_code()
    
    # 업데이트
    artist.login_code = new_code
    artist.login_code_created_at = datetime.now()
    
    db.commit()
    db.refresh(artist)
    
    return artist


# 전체 작가 코드 일괄 생성
@router.post(
    "/batch/generate-login-codes",
    summary="전체 작가 로그인 코드 일괄 생성",
    description="로그인 코드가 없는 모든 작가에게 코드를 생성합니다. (관리자 전용)",
)
def batch_generate_login_codes(
    db: Session = Depends(get_db),
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """
    전체 작가 로그인 코드 일괄 생성 (관리자)

    Args:
        x_api_key: 관리자 API Key

    Returns:
        생성된 코드 개수 및 메시지

    Raises:
        403: 권한 없음
    """
    # Admin 인증
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    # 코드가 없는 작가들 조회
    artists_without_code = db.query(Artist).filter(
        Artist.login_code.is_(None)
    ).all()
    
    if not artists_without_code:
        return {
            "message": "모든 작가가 이미 로그인 코드를 가지고 있습니다",
            "count": 0
        }
    
    count = 0
    used_codes = set()
    
    for artist in artists_without_code:
        # 새 코드 생성
        new_code = generate_login_code()
        
        # 중복 확인 (DB + 현재 배치)
        while new_code in used_codes or db.query(Artist).filter(
            Artist.login_code == new_code
        ).first():
            new_code = generate_login_code()
        
        used_codes.add(new_code)
        
        # 업데이트
        artist.login_code = new_code
        artist.login_code_created_at = datetime.now()
        count += 1
    
    db.commit()
    
    return {
        "message": f"{count}명의 작가에게 로그인 코드를 생성했습니다",
        "count": count
    }