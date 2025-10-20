# app/api/v1/endpoints/artists.py
from typing import List

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.schemas.artist import ArtistCreate, ArtistResponse, ArtistUpdate
from fastapi import APIRouter, Depends, HTTPException, status

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
    description="새 작가를 등록합니다. (관리자 전용, API Key 필요)",
)
def create_artist(artist_data: ArtistCreate, db: Session = Depends(get_db)):
    """
    작가 생성 (관리자)

    Args:
        artist_data: 작가 생성 데이터

    Returns:
        ArtistResponse: 생성된 작가 정보

    Note:
        UUID는 서버에서 자동 생성
    """
    new_artist = Artist(**artist_data.model_dump())
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist


@router.put(
    "/{artist_id}",
    response_model=ArtistResponse,
    summary="작가 수정",
    description="작가 정보를 수정합니다. (관리자 전용, API Key 필요)",
)
def update_artist(
    artist_id: int, artist_data: ArtistUpdate, db: Session = Depends(get_db)
):
    """
    작가 정보 수정 (관리자)

    Args:
        artist_id: 작가 ID
        artist_data: 수정 데이터

    Returns:
        ArtistResponse: 수정된 작가 정보

    Raises:
        404: 작가를 찾을 수 없음
    """
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
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    """
    작가 삭제 (관리자)

    Args:
        artist_id: 작가 ID

    Raises:
        404: 작가를 찾을 수 없음
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
        )

    db.delete(artist)
    db.commit()
    return None
