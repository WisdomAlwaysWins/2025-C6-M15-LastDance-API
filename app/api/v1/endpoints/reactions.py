# app/api/v1/endpoints/reactions.py
from datetime import datetime
import json
import logging
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal, get_db
from app.models.artwork import Artwork
from app.models.exhibition import Exhibition
from app.models.reaction import Reaction
from app.models.tag import Tag
from app.models.visit_history import VisitHistory
from app.schemas.reaction import (
    ReactionDetail,
    ReactionResponse,
)
from app.utils.notification_helper import (
    notify_artist_reply_to_visitor,
    notify_reaction_to_artist,
)
from app.utils.s3_client import s3_client
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
    Header,
)

from app.models.artist import Artist
from app.models.artist_reaction_emoji import ArtistReactionEmoji
from app.schemas.artist_reaction_emoji import (
    ArtistReactionEmojiCreate,
    ArtistReactionEmojiResponse,
)
from app.models.artist_reaction_message import ArtistReactionMessage
from app.schemas.artist_reaction_message import (
    ArtistReactionMessageCreate,
    ArtistReactionMessageResponse,
)

from app.constants.emojis import is_valid_emoji_type

router = APIRouter(prefix="/reactions", tags=["Reactions"])

logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=List[ReactionResponse],
    summary="반응 목록 조회",
    description="반응 목록을 조회합니다. artwork_id, visitor_id, visit_id로 필터링 가능합니다.",
)
def get_reactions(
    artwork_id: Optional[int] = Query(None, description="작품 ID로 필터링"),
    visitor_id: Optional[int] = Query(None, description="관람객 ID로 필터링"),
    visit_id: Optional[int] = Query(None, description="방문 기록 ID로 필터링"),
    db: Session = Depends(get_db),
):
    """
    반응 목록 조회 (가벼운 버전)

    Args:
        artwork_id: 작품 ID로 필터링
        visitor_id: 관람객 ID로 필터링
        visit_id: 방문 기록 ID로 필터링

    Returns:
        List[ReactionResponse]: 반응 목록 (artwork_title, visitor_name 포함)
    """
    logger.info(f"반응 목록 조회 시작 (artwork_id={artwork_id}, visitor_id={visitor_id}, visit_id={visit_id})")
    
    query = db.query(Reaction).options(
        joinedload(Reaction.artwork),
        joinedload(Reaction.visitor),
        joinedload(Reaction.tags).joinedload(Tag.category),
    )

    # 필터링
    if artwork_id:
        query = query.filter(Reaction.artwork_id == artwork_id)
    if visitor_id:
        query = query.filter(Reaction.visitor_id == visitor_id)
    if visit_id:
        query = query.filter(Reaction.visit_id == visit_id)

    reactions = query.order_by(Reaction.created_at.desc()).all()

    # ReactionResponse 형식으로 변환
    result = []
    for reaction in reactions:
        result.append(
            {
                "id": reaction.id,
                "artwork_id": reaction.artwork_id,
                "artwork_title": reaction.artwork.title if reaction.artwork else "",
                "visitor_id": reaction.visitor_id,
                "visitor_name": reaction.visitor.name if reaction.visitor else None,
                "visit_id": reaction.visit_id,
                "comment": reaction.comment,
                "image_url": reaction.image_url,
                "tags": reaction.tags,
                "created_at": reaction.created_at,
                "updated_at": reaction.updated_at,
            }
        )

    logger.info(f"✅ 반응 {len(result)}개 조회 완료")
    return result


@router.get(
    "/{reaction_id}",
    response_model=ReactionDetail,
    summary="반응 상세 조회",
    description="반응 ID로 상세 정보를 조회합니다. 작품, 관람객, 방문 기록, 태그, 작가 이모지, 작가 메시지 포함",
)
def get_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 상세 조회 (전체 정보)
    """
    logger.info(f"반응 상세 조회 시작: ID {reaction_id}")
    
    reaction = (
        db.query(Reaction)
        .options(
            joinedload(Reaction.artwork).joinedload(Artwork.artist),
            joinedload(Reaction.visitor),
            joinedload(Reaction.visit).joinedload(VisitHistory.exhibition),
            joinedload(Reaction.tags).joinedload(Tag.category),
            joinedload(Reaction.artist_emojis).joinedload(ArtistReactionEmoji.artist), 
            joinedload(Reaction.artist_messages).joinedload(ArtistReactionMessage.artist), 
        )
        .filter(Reaction.id == reaction_id)
        .first()
    )

    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )

    # 작가 이모지 포맷팅
    artist_emojis = []
    for emoji in reaction.artist_emojis:
        artist_emojis.append({
            "id": emoji.id,
            "artist_id": emoji.artist_id,
            "artist_name": emoji.artist.name if emoji.artist else "",
            "emoji_type": emoji.emoji_type,
            "created_at": emoji.created_at,
        })

    # 작가 메시지 포맷팅(오래된 순)
    artist_messages = []
    for message in sorted(reaction.artist_messages, key=lambda x: x.created_at):
        artist_messages.append({
            "id": message.id,
            "artist_id": message.artist_id,
            "artist_name": message.artist.name if message.artist else "",
            "message": message.message,
            "created_at": message.created_at,
        })

    # ReactionDetail 형식으로 변환
    result = {
        "id": reaction.id,
        "artwork_id": reaction.artwork_id,
        "artwork": (
            {
                "id": reaction.artwork.id,
                "title": reaction.artwork.title,
                "artist_id": reaction.artwork.artist_id,
                "artist_name": (
                    reaction.artwork.artist.name if reaction.artwork.artist else ""
                ),
                "description": reaction.artwork.description,
                "year": reaction.artwork.year,
                "thumbnail_url": reaction.artwork.thumbnail_url,
                "reaction_count": (
                    len(reaction.artwork.reactions) if reaction.artwork else 0
                ),
                "created_at": reaction.artwork.created_at,
                "updated_at": reaction.artwork.updated_at,
            }
            if reaction.artwork
            else None
        ),
        "visitor_id": reaction.visitor_id,
        "visitor": reaction.visitor,
        "visit_id": reaction.visit_id,
        "visit": (
            {
                "id": reaction.visit.id,
                "exhibition_id": reaction.visit.exhibition_id,
                "exhibition_title": (
                    reaction.visit.exhibition.title if reaction.visit.exhibition else ""
                ),
                "visited_at": reaction.visit.visited_at,
            }
            if reaction.visit
            else None
        ),
        "comment": reaction.comment,
        "image_url": reaction.image_url,
        "tags": reaction.tags,
        "artist_emojis": artist_emojis, 
        "artist_messages": artist_messages,
        "created_at": reaction.created_at,
        "updated_at": reaction.updated_at,
    }

    logger.info(f"✅ 반응 조회 완료: ID {reaction_id}, 이모지 {len(artist_emojis)}개, 메시지 {len(artist_messages)}개")
    return result


@router.post(
    "",
    response_model=ReactionDetail,
    status_code=status.HTTP_201_CREATED,
    summary="반응 생성",
    description="새 반응을 생성합니다. 이미지 업로드 및 태그 연결 포함.",
)
async def create_reaction(
    background_tasks: BackgroundTasks,
    visitor_id: int = Form(...),
    artwork_id: int = Form(...),
    visit_id: Optional[int] = Form(None),
    comment: Optional[str] = Form(None),
    tag_ids: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    반응 생성 (이미지 포함)

    Args:
        visitor_id: 관람객 ID
        artwork_id: 작품 ID
        visit_id: 방문 기록 ID (선택)
        comment: 코멘트 (선택)
        tag_ids: 태그 ID 배열 JSON string (예: "[1,3,5]")
        image: 촬영한 이미지 파일

    Returns:
        ReactionDetail: 생성된 반응 정보 (작품, 관람객, 태그, 이미지 포함)

    Raises:
        404: 존재하지 않는 artwork_id, visitor_id, visit_id, tag_ids
        500: S3 업로드 실패

    Note:
        이미지는 S3 reactions 폴더에 저장됨
        visit_id가 있으면: reactions/{env}/exhibition_{id}/visitor_{id}_{timestamp}.jpg
        visit_id가 없으면: reactions/{uuid}.jpg
    """
    logger.info(f"반응 생성 시작: visitor_id={visitor_id}, artwork_id={artwork_id}, visit_id={visit_id}")

    # Artwork 존재 여부 확인
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        logger.warning(f"작품 ID {artwork_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {artwork_id}를 찾을 수 없습니다",
        )

    # Visitor 존재 여부 확인
    from app.models.visitor import Visitor

    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        logger.warning(f"관람객 ID {visitor_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )

    # Visit 존재 여부 확인 (선택) & exhibition_id 추출
    exhibition_id = None
    if visit_id:
        visit = db.query(VisitHistory).filter(VisitHistory.id == visit_id).first()
        if not visit:
            logger.warning(f"방문 기록 ID {visit_id} 찾을 수 없음")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"방문 기록 ID {visit_id}를 찾을 수 없습니다",
            )
        exhibition_id = visit.exhibition_id
        logger.info(f"Exhibition ID 추출: {exhibition_id} (Visit ID: {visit_id})")

    # S3에 이미지 업로드
    try:
        logger.info(f"S3 업로드 시작: {image.filename}")
        image_url = await s3_client.upload_file(
            file=image,
            folder="reactions",
            exhibition_id=exhibition_id,  # visit_id가 있으면 전시 ID 전달
            visitor_id=visitor_id,  # 관람객 ID 전달
        )
        logger.info(f"✅ S3 업로드 성공: {image_url}")
    except Exception as e:
        logger.error(f"❌ S3 업로드 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 업로드 실패: {str(e)}",
        )

    # Reaction 생성
    new_reaction = Reaction(
        visitor_id=visitor_id,
        artwork_id=artwork_id,
        visit_id=visit_id,
        comment=comment,
        image_url=image_url,
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)

    # Tag 연결 (M:N)
    if tag_ids:
        try:
            tag_id_list = json.loads(tag_ids)
            logger.info(f"태그 연결 시도: {len(tag_id_list)}개")
            tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()

            # 존재하지 않는 태그 확인
            found_ids = {tag.id for tag in tags}
            missing_ids = set(tag_id_list) - found_ids
            if missing_ids:
                logger.warning(f"태그 ID {sorted(missing_ids)} 찾을 수 없음")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"태그 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                )

            new_reaction.tags.extend(tags)
            db.commit()
            db.refresh(new_reaction)
            logger.info(f"✅ 태그 {len(tags)}개 연결 완료")
        except json.JSONDecodeError:
            logger.error("태그 JSON 파싱 실패")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tag_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    logger.info(f"✅ 반응 생성 완료: ID {new_reaction.id}")

    # 생성 후 상세 정보 조회하여 반환
    result = get_reaction(new_reaction.id, db)
    
    # 백그라운드에서 작가에게 푸시 전송
    if artwork and artwork.artist:
        # 전시 정보 찾기
        exhibition = None
        
        # 1. visit_id로 전시 찾기
        if visit_id and visit:
            exhibition = (
                db.query(Exhibition)
                .filter(Exhibition.id == visit.exhibition_id)
                .first()
            )
        
        # 2. visit_id 없으면 작품의 첫 번째 전시 사용
        if not exhibition:
            artwork_with_exhibitions = (
                db.query(Artwork)
                .options(joinedload(Artwork.exhibitions))
                .filter(Artwork.id == artwork_id)
                .first()
            )
            if artwork_with_exhibitions and artwork_with_exhibitions.exhibitions:
                exhibition = artwork_with_exhibitions.exhibitions[0]
        
        # 3. 전시 정보 있으면 푸시 전송
        if exhibition:
            background_tasks.add_task(
                notify_reaction_to_artist,
                db=SessionLocal(),
                artist_id=artwork.artist.id,
                exhibition_id=exhibition.id,
                exhibition_title=exhibition.title,
                artwork_id=artwork.id,
                artwork_title=artwork.title,
                reaction_id=new_reaction.id,
                created_at=new_reaction.created_at,
            )
            logger.info(
                f"🔔 작가 ID {artwork.artist.id}에게 푸시 알림 예약 (전시: '{exhibition.title}')"
            )
    
    return result


@router.put(
    "/{reaction_id}",
    response_model=ReactionDetail,
    summary="반응 수정",
    description="반응의 코멘트, 이미지, 태그를 수정합니다. 이미지 수정 시 기존 S3 이미지는 삭제됩니다.",
)
async def update_reaction(
    reaction_id: int,
    comment: Optional[str] = Form(None),
    tag_ids: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """
    반응 수정 (이미지 교체 포함)

    Args:
        reaction_id: 반응 ID
        comment: 코멘트 (선택)
        tag_ids: 태그 ID 배열 JSON string (예: "[1,3,5]") (선택)
        image: 새 이미지 파일 (선택)

    Returns:
        ReactionDetail: 수정된 반응 정보 (전체)

    Raises:
        404: 반응을 찾을 수 없음
        400: comment와 tag_ids 둘 다 비움

    Note:
        - 이미지를 새로 업로드하면 기존 S3 이미지는 자동 삭제됩니다
        - tag_ids는 JSON 배열 문자열로 전달 (예: "[1,2,3]")
    """
    logger.info(f"반응 수정 시작: ID {reaction_id}")
    
    reaction = (
        db.query(Reaction)
        .options(joinedload(Reaction.visit))
        .filter(Reaction.id == reaction_id)
        .first()
    )

    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다",
        )

    updated_fields = []

    # comment 수정
    if comment is not None:
        reaction.comment = comment  # type: ignore
        updated_fields.append("코멘트")

    # image 수정 (새 이미지 업로드 시)
    if image is not None:
        logger.info(f"이미지 교체 시작: {image.filename}")
        
        # 기존 S3 이미지 삭제
        old_image_url = reaction.image_url
        if old_image_url:
            try:
                s3_client.delete_file(str(old_image_url))
                logger.info(f"✅ 기존 이미지 삭제 성공")
            except Exception as e:
                logger.warning(f"⚠️  기존 이미지 삭제 실패 (계속 진행): {e}")

        # 새 이미지 업로드
        try:
            # visit 정보로부터 exhibition_id 추출
            exhibition_id = None
            if reaction.visit:
                exhibition_id = reaction.visit.exhibition_id

            new_image_url = await s3_client.upload_file(
                file=image,
                folder="reactions",
                exhibition_id=exhibition_id,
                visitor_id=reaction.visitor_id,
            )
            reaction.image_url = new_image_url  # type: ignore
            logger.info(f"✅ 새 이미지 업로드 성공: {new_image_url}")
            updated_fields.append("이미지")
        except Exception as e:
            logger.error(f"❌ S3 업로드 실패: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 실패: {str(e)}",
            )

    # tag_ids 수정
    if tag_ids is not None:
        try:
            # 기존 태그 삭제
            reaction.tags.clear()

            # 새 태그 추가
            if tag_ids:
                tag_id_list = json.loads(tag_ids)
                logger.info(f"태그 수정: {len(tag_id_list)}개")
                tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()

                # 존재하지 않는 태그 체크
                found_ids = {tag.id for tag in tags}
                missing_ids = set(tag_id_list) - found_ids
                if missing_ids:
                    logger.warning(f"태그 ID {sorted(missing_ids)} 찾을 수 없음")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"태그 ID {sorted(missing_ids)}를 찾을 수 없습니다",
                    )

                reaction.tags.extend(tags)
                updated_fields.append(f"태그 {len(tags)}개")
        except json.JSONDecodeError:
            logger.error("태그 JSON 파싱 실패")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tag_ids는 유효한 JSON 배열 문자열이어야 합니다",
            )

    # Validation: comment와 tag_ids 둘 다 비어있으면 에러
    if not reaction.comment and not reaction.tags:
        logger.warning("코멘트와 태그 모두 비어있음")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="코멘트 또는 태그 중 하나는 필수입니다",
        )

    db.commit()
    db.refresh(reaction)

    logger.info(f"✅ 반응 수정 완료: ID {reaction_id} ({', '.join(updated_fields) if updated_fields else '변경 없음'})")

    # 수정 후 상세 정보 조회하여 반환
    return get_reaction(reaction_id, db)


@router.delete(
    "/{reaction_id}",
    status_code=204,
    summary="반응 삭제",
    description="반응을 삭제합니다. 연결된 S3 이미지도 함께 삭제됩니다.",
)
async def delete_reaction(reaction_id: int, db: Session = Depends(get_db)):
    """
    반응 삭제 (촬영한 이미지도 함께 삭제)

    Args:
        reaction_id: 반응 ID

    Raises:
        404: 반응을 찾을 수 없음

    Note:
        S3에 저장된 이미지도 함께 삭제됩니다
    """
    logger.info(f"반응 삭제 시작: ID {reaction_id}")
    
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="반응을 찾을 수 없습니다"
        )

    # S3에서 이미지 삭제 (있는 경우)
    if reaction.image_url:
        try:
            s3_client.delete_file(str(reaction.image_url))
            logger.info(f"✅ S3 이미지 삭제 성공")
        except Exception as e:
            logger.warning(f"⚠️  S3 이미지 삭제 실패 (계속 진행): {e}")

    # DB에서 반응 삭제
    db.delete(reaction)
    db.commit()

    logger.info(f"✅ 반응 삭제 완료: ID {reaction_id}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# 작가 이모지 남기기 (UUID 사용)
@router.post(
    "/{reaction_id}/artist-emoji",
    response_model=ArtistReactionEmojiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="작가 이모지 남기기",
    description="작가가 관람객의 반응에 이모지를 남깁니다.",
)
async def create_artist_emoji(
    reaction_id: int,
    emoji_data: ArtistReactionEmojiCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_artist_uuid: str = Header(..., alias="X-Artist-UUID"),
):
    """
    작가 이모지 생성
    
    Args:
        reaction_id: 반응 ID
        emoji_data: 이모지 데이터
        x_artist_uuid: 작가 UUID (헤더)
    """
    logger.info(f"작가 이모지 생성 시도: 반응 ID {reaction_id}, 작가 UUID {x_artist_uuid[:8]}..., 이모지 {emoji_data.emoji_type}")
    
    # UUID로 작가 조회
    artist = db.query(Artist).filter(Artist.uuid == x_artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {x_artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작가를 찾을 수 없습니다"
        )
    
    # 반응 존재 확인 + joinedload로 관련 정보 가져오기
    reaction = (
        db.query(Reaction)
        .options(
            joinedload(Reaction.visit).joinedload(VisitHistory.exhibition),
            joinedload(Reaction.artwork)
        )
        .filter(Reaction.id == reaction_id)
        .first()
    )
    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다"
        )
    
    # 이모지 타입 검증
    if not is_valid_emoji_type(emoji_data.emoji_type):
        logger.warning(f"허용되지 않은 이모지 타입: {emoji_data.emoji_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않은 이모지 타입입니다"
        )
    
    # 이미 이모지를 남겼는지 확인
    existing_emoji = db.query(ArtistReactionEmoji).filter(
        ArtistReactionEmoji.artist_id == artist.id,
        ArtistReactionEmoji.reaction_id == reaction_id
    ).first()
    
    if existing_emoji:
        logger.warning(f"중복 이모지 생성 시도: 작가 '{artist.name}', 반응 ID {reaction_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 이 반응에 이모지를 남겼습니다"
        )
    
    # 이모지 생성
    new_emoji = ArtistReactionEmoji(
        artist_id=artist.id,
        reaction_id=reaction_id,
        emoji_type=emoji_data.emoji_type,
    )
    
    db.add(new_emoji)
    db.commit()
    db.refresh(new_emoji)
    
    logger.info(f"✅ 작가 이모지 생성 완료: ID {new_emoji.id}, 작가 '{artist.name}', 반응 ID {reaction_id}, 타입 {emoji_data.emoji_type}")
    
    # 관객에게 푸시 알림 전송 (백그라운드)
    if reaction.visit and reaction.visit.exhibition:
        background_tasks.add_task(
            notify_artist_reply_to_visitor,
            db=SessionLocal(),
            visitor_id=reaction.visitor_id,
            exhibition_id=reaction.visit.exhibition.id,
            visit_history_id=reaction.visit_id,
            exhibition_title=reaction.visit.exhibition.title,
            artwork_id=reaction.artwork_id,
            reaction_id=reaction.id,
            reply_created_at=new_emoji.created_at,
        )
        logger.info(f"🔔 관객 ID {reaction.visitor_id}에게 이모지 응답 푸시 알림 예약")
    
    return new_emoji


# 작가 이모지 삭제 (UUID 사용)
@router.delete(
    "/{reaction_id}/artist-emoji",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="작가 이모지 삭제",
    description="작가가 자신이 남긴 이모지를 삭제합니다.",
)
def delete_artist_emoji(
    reaction_id: int,
    db: Session = Depends(get_db),
    x_artist_uuid: str = Header(..., alias="X-Artist-UUID"),  # UUID 사용
):
    """
    작가 이모지 삭제
    """
    logger.info(f"작가 이모지 삭제 시도: 반응 ID {reaction_id}, 작가 UUID {x_artist_uuid[:8]}...")
    
    # UUID로 작가 조회
    artist = db.query(Artist).filter(Artist.uuid == x_artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {x_artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작가를 찾을 수 없습니다"
        )
    
    # 이모지 조회
    emoji = db.query(ArtistReactionEmoji).filter(
        ArtistReactionEmoji.artist_id == artist.id,
        ArtistReactionEmoji.reaction_id == reaction_id
    ).first()
    
    if not emoji:
        logger.warning(f"이모지 찾을 수 없음: 작가 '{artist.name}', 반응 ID {reaction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이모지를 찾을 수 없습니다"
        )
    
    emoji_id = emoji.id
    emoji_type = emoji.emoji_type
    
    db.delete(emoji)
    db.commit()
    
    logger.info(f"✅ 작가 이모지 삭제 완료: ID {emoji_id}, 작가 '{artist.name}', 타입 {emoji_type}")
    
    return None


@router.post(
    "/{reaction_id}/artist-messages",
    response_model=ArtistReactionMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="작가 메시지 보내기",
    description="작가가 관람객의 반응에 메시지를 보냅니다. (10자 이내, 여러 번 가능)",
)
async def create_artist_message(
    reaction_id: int,
    message_data: ArtistReactionMessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_artist_uuid: str = Header(..., alias="X-Artist-UUID"),
):
    """
    작가 메시지 생성
    
    Args:
        reaction_id: 반응 ID
        message_data: 메시지 데이터
        x_artist_uuid: 작가 UUID (헤더)
    
    Returns:
        생성된 메시지 정보
    
    Raises:
        401: 인증 실패
        404: 반응 또는 작가를 찾을 수 없음
        400: 메시지 길이 초과
    """
    logger.info(f"작가 메시지 생성 시도: 반응 ID {reaction_id}, 작가 UUID {x_artist_uuid[:8]}..., 메시지 길이 {len(message_data.message)}자")
    
    # UUID로 작가 조회
    artist = db.query(Artist).filter(Artist.uuid == x_artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {x_artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="작가를 찾을 수 없습니다"
        )
    
    # 반응 존재 확인 + joinedload로 관련 정보 가져오기
    reaction = (
        db.query(Reaction)
        .options(
            joinedload(Reaction.visit).joinedload(VisitHistory.exhibition),
            joinedload(Reaction.artwork)
        )
        .filter(Reaction.id == reaction_id)
        .first()
    )
    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다"
        )
    
    # 메시지 생성
    new_message = ArtistReactionMessage(
        artist_id=artist.id,
        reaction_id=reaction_id,
        message=message_data.message,
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    logger.info(f"✅ 작가 메시지 생성 완료: ID {new_message.id}, 작가 '{artist.name}', 반응 ID {reaction_id}")
    
    # 관객에게 푸시 알림 전송 (백그라운드)
    if reaction.visit and reaction.visit.exhibition:
        background_tasks.add_task(
            notify_artist_reply_to_visitor,
            db=SessionLocal(),
            visitor_id=reaction.visitor_id,
            exhibition_id=reaction.visit.exhibition.id,
            visit_history_id=reaction.visit_id,
            exhibition_title=reaction.visit.exhibition.title,
            artwork_id=reaction.artwork_id,
            reaction_id=reaction.id,
            reply_created_at=new_message.created_at,
        )
        logger.info(
            f"🔔 관객 ID {reaction.visitor_id}에게 메시지 응답 푸시 알림 예약 "
            f"(전시: '{reaction.visit.exhibition.title}')"
        )
    
    return new_message


@router.get(
    "/{reaction_id}/artist-messages",
    response_model=List[ArtistReactionMessageResponse],
    summary="작가 메시지 목록 조회",
    description="특정 반응에 달린 작가 메시지들을 조회합니다. (시간순 정렬)",
)
def get_artist_messages(
    reaction_id: int,
    db: Session = Depends(get_db),
):
    """
    작가 메시지 목록 조회
    
    Args:
        reaction_id: 반응 ID
    
    Returns:
        메시지 목록 (오래된 순)
    
    Raises:
        404: 반응을 찾을 수 없음
    """
    logger.info(f"작가 메시지 목록 조회: 반응 ID {reaction_id}")
    
    # 반응 존재 확인
    reaction = db.query(Reaction).filter(Reaction.id == reaction_id).first()
    if not reaction:
        logger.warning(f"반응 ID {reaction_id} 찾을 수 없음")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"반응 ID {reaction_id}를 찾을 수 없습니다"
        )
    
    # 메시지 조회 (오래된 순)
    messages = db.query(ArtistReactionMessage).filter(
        ArtistReactionMessage.reaction_id == reaction_id
    ).order_by(ArtistReactionMessage.created_at.asc()).all()
    
    logger.info(f"✅ 작가 메시지 {len(messages)}개 조회 완료")
    
    return messages