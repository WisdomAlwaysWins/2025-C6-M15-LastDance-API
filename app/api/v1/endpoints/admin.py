from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import json

from app.database import get_db
from app.models.exhibition import Exhibition
from app.models.artwork import Artwork
from app.models.tag import Tag
from app.schemas.exhibition import ExhibitionCreate, ExhibitionResponse
from app.schemas.artwork import ArtworkResponse
from app.schemas.tag import TagCreate, TagResponse
from app.utils.s3_client import s3_client

router = APIRouter()


# ========== 전시 관리 ==========

@router.put("/exhibitions/{exhibition_id}/poster", response_model=ExhibitionResponse)
async def update_exhibition_poster(
    exhibition_id: int,
    poster: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    전시 포스터 이미지 업데이트 (관리자용)
    """
    db_exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    # 기존 포스터 삭제 (있는 경우)
    if db_exhibition.poster_url:
        s3_client.delete_file(db_exhibition.poster_url)
    
    # 새 포스터 업로드
    file_content = await poster.read()
    file_extension = poster.filename.split(".")[-1]
    
    poster_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_extension,
        folder="posters"
    )
    
    if not poster_url:
        raise HTTPException(status_code=500, detail="Failed to upload poster to S3")
    
    db_exhibition.poster_url = poster_url
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

@router.post("/exhibitions/", response_model=ExhibitionResponse, status_code=201)
async def create_exhibition(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    artist_names: str = Form(...),  # JSON 문자열로 받음 (예: '["김작가", "이작가"]')
    start_date: date = Form(...),
    end_date: date = Form(...),
    poster: Optional[UploadFile] = File(None),  # 포스터 이미지 (선택)
    db: Session = Depends(get_db)
):
    """
    전시 등록 (관리자용)
    포스터 이미지는 선택 사항
    """
    import json
    
    # artist_names를 JSON 파싱
    try:
        artist_names_list = json.loads(artist_names)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="artist_names must be a valid JSON array")
    
    # 포스터 이미지 업로드 (있는 경우만)
    poster_url = None
    if poster:
        file_content = await poster.read()
        file_extension = poster.filename.split(".")[-1]
        
        poster_url = s3_client.upload_file(
            file_content=file_content,
            file_extension=file_extension,
            folder="posters"
        )
        
        if not poster_url:
            raise HTTPException(status_code=500, detail="Failed to upload poster to S3")
    
    # 전시 생성
    db_exhibition = Exhibition(
        title=title,
        description=description,
        location=location,
        poster_url=poster_url,
        artist_names=artist_names_list,
        start_date=start_date,
        end_date=end_date
    )
    
    db.add(db_exhibition)
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition

@router.put("/exhibitions/{exhibition_id}", response_model=ExhibitionResponse)
async def update_exhibition(
    exhibition_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    poster_url: Optional[str] = None,
    artist_names: Optional[List[str]] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    전시 수정 (관리자용)
    """
    db_exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not db_exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    # 전달된 필드만 업데이트
    if title is not None:
        db_exhibition.title = title
    if description is not None:
        db_exhibition.description = description
    if location is not None:
        db_exhibition.location = location
    if poster_url is not None:
        db_exhibition.poster_url = poster_url
    if artist_names is not None:
        db_exhibition.artist_names = artist_names
    if start_date is not None:
        db_exhibition.start_date = start_date
    if end_date is not None:
        db_exhibition.end_date = end_date
    
    db.commit()
    db.refresh(db_exhibition)
    return db_exhibition


# ========== 작품 관리 ==========

@router.post("/artworks/", response_model=ArtworkResponse, status_code=201)
async def create_artwork(
    title: str = Form(...),
    artist_name: str = Form(...),
    exhibition_id: int = Form(...),
    description: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    작품 등록 + 이미지 업로드 (관리자용)
    """
    # 전시 존재 확인
    exhibition = db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
    if not exhibition:
        raise HTTPException(status_code=404, detail="Exhibition not found")
    
    # 이미지 업로드 (S3)
    file_content = await image.read()
    file_extension = image.filename.split(".")[-1]
    
    image_url = s3_client.upload_file(
        file_content=file_content,
        file_extension=file_extension,
        folder="artworks"
    )
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")
    
    # 작품 생성
    db_artwork = Artwork(
        title=title,
        artist_name=artist_name,
        description=description,
        year=year,
        image_url=image_url,
        exhibition_id=exhibition_id
    )
    
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


@router.put("/artworks/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    title: Optional[str] = Form(None),
    artist_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    작품 수정 (관리자용)
    이미지를 새로 업로드하면 기존 이미지는 S3에서 삭제
    """
    db_artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # 필드 업데이트
    if title is not None:
        db_artwork.title = title
    if artist_name is not None:
        db_artwork.artist_name = artist_name
    if description is not None:
        db_artwork.description = description
    if year is not None:
        db_artwork.year = year
    
    # 이미지 교체
    if image is not None:
        # 기존 이미지 삭제
        s3_client.delete_file(db_artwork.image_url)
        
        # 새 이미지 업로드
        file_content = await image.read()
        file_extension = image.filename.split(".")[-1]
        
        new_image_url = s3_client.upload_file(
            file_content=file_content,
            file_extension=file_extension,
            folder="artworks"
        )
        
        if not new_image_url:
            raise HTTPException(status_code=500, detail="Failed to upload new image to S3")
        
        db_artwork.image_url = new_image_url
    
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


@router.delete("/artworks/{artwork_id}", status_code=204)
async def delete_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    """
    작품 삭제 (관리자용)
    S3 이미지도 함께 삭제
    """
    db_artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # S3 이미지 삭제
    s3_client.delete_file(db_artwork.image_url)
    
    # DB에서 삭제
    db.delete(db_artwork)
    db.commit()
    return None


# ========== 태그 관리 ==========

@router.post("/tags/", response_model=TagResponse, status_code=201)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """
    태그 등록 (관리자용)
    """
    # 중복 확인
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/tags/", response_model=List[TagResponse])
async def list_tags(db: Session = Depends(get_db)):
    """
    태그 목록 조회
    """
    tags = db.query(Tag).all()
    return tags