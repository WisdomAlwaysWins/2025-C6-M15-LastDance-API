"""
Invitation Router

초대장 API 엔드포인트
"""

import logging
from typing import List
import uuid

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.artist import Artist
from app.models.exhibition import Exhibition
from app.models.invitation import Invitation
from app.models.invitation_interest import InvitationInterest
from app.models.visitor import Visitor
from app.schemas.invitation import (
    ArtistInInvitation,
    ExhibitionInInvitation,
    InvitationCreate,
    InvitationInterestCreate,
    InvitationInterestResponse,
    InvitationPublicResponse,
    InvitationResponse,
    VenueInInvitation,
)
from fastapi import APIRouter, Depends, Header, HTTPException, Response

router = APIRouter(prefix="/invitations", tags=["Invitations"])
logger = logging.getLogger(__name__)


# ============================================================================
# 작가용 API (X-Artist-UUID 필요)
# ============================================================================


@router.post(
    "/",
    response_model=InvitationResponse,
    status_code=201,
    summary="초대장 생성",
    description="""
    작가가 특정 전시에 대한 초대장을 생성합니다.
    
    - 한 전시당 작가 1명당 초대장 1개만 생성 가능
    - 중복 생성 시도 시 409 에러 반환
    - 생성된 초대장은 고유 코드와 딥링크를 포함
    """,
)
async def create_invitation(
    data: InvitationCreate,
    db: Session = Depends(get_db),
    artist_uuid: str = Header(..., alias="X-Artist-UUID"),
):
    logger.info(
        f"초대장 생성 시도: 작가 UUID {artist_uuid[:8]}..., 전시 ID {data.exhibition_id}"
    )

    # 작가 확인
    artist = db.query(Artist).filter(Artist.uuid == artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(status_code=401, detail="Invalid artist UUID")

    # 전시 확인
    exhibition = (
        db.query(Exhibition).filter(Exhibition.id == data.exhibition_id).first()
    )
    if not exhibition:
        logger.warning(f"전시 ID {data.exhibition_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Exhibition not found")

    # 중복 초대장 체크
    existing_invitation = (
        db.query(Invitation)
        .filter(
            Invitation.exhibition_id == data.exhibition_id,
            Invitation.artist_id == artist.id,
        )
        .first()
    )

    if existing_invitation:
        logger.warning(
            f"중복 초대장 생성 시도: 작가 '{artist.name}', 전시 '{exhibition.title}'"
        )
        raise HTTPException(
            status_code=409, detail="해당 전시에 대한 초대장이 이미 존재합니다."
        )

    # 초대장 생성
    invitation_code = str(uuid.uuid4())
    invitation = Invitation(
        code=invitation_code,
        artist_id=artist.id,
        exhibition_id=data.exhibition_id,
        message=data.message,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    logger.info(
        f"✅ 초대장 생성 완료: ID {invitation.id}, 코드 {invitation_code[:8]}..., 작가 '{artist.name}', 전시 '{exhibition.title}'"
    )

    # Response 생성
    return _build_invitation_response(invitation, db)


@router.get(
    "/",
    response_model=List[InvitationResponse],
    summary="내 초대장 목록 조회",
    description="""
    작가 본인이 생성한 모든 초대장 목록을 조회합니다.
    
    - 최신 생성순으로 정렬
    - 각 초대장의 방문 통계(view_count) 포함
    - 딥링크 및 공유용 링크 포함
    """,
)
async def get_my_invitations(
    db: Session = Depends(get_db), artist_uuid: str = Header(..., alias="X-Artist-UUID")
):
    logger.info(f"초대장 목록 조회: 작가 UUID {artist_uuid[:8]}...")

    # 작가 확인
    artist = db.query(Artist).filter(Artist.uuid == artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(status_code=401, detail="Invalid artist UUID")

    # 초대장 목록 조회
    invitations = (
        db.query(Invitation)
        .filter(Invitation.artist_id == artist.id)
        .order_by(Invitation.created_at.desc())
        .all()
    )

    logger.info(f"✅ 초대장 {len(invitations)}개 조회 완료: 작가 '{artist.name}'")

    # Response 생성
    return [_build_invitation_response(inv, db) for inv in invitations]


@router.get(
    "/{invitation_id}",
    response_model=InvitationResponse,
    summary="초대장 상세 조회 (작가용)",
    description="""
    작가가 특정 초대장의 상세 정보를 조회합니다.
    
    - 본인이 생성한 초대장만 조회 가능
    - view_count 포함
    - 딥링크 및 공유용 링크 포함
    """,
)
async def get_invitation_detail(
    invitation_id: int,
    db: Session = Depends(get_db),
    artist_uuid: str = Header(..., alias="X-Artist-UUID"),
):
    logger.info(f"초대장 상세 조회: ID {invitation_id}, 작가 UUID {artist_uuid[:8]}...")

    # 작가 확인
    artist = db.query(Artist).filter(Artist.uuid == artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(status_code=401, detail="Invalid artist UUID")

    # 초대장 확인
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        logger.warning(f"초대장 ID {invitation_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Invitation not found")

    # 권한 확인 (본인 것만 조회 가능)
    if invitation.artist_id != artist.id:
        logger.warning(
            f"권한 없음: 초대장 ID {invitation_id}, 요청 작가 '{artist.name}', 소유 작가 ID {invitation.artist_id}"
        )
        raise HTTPException(status_code=403, detail="Not your invitation")

    logger.info(f"✅ 초대장 조회 완료: ID {invitation_id}, 작가 '{artist.name}'")

    # Response 생성
    return _build_invitation_response(invitation, db)


@router.delete(
    "/{invitation_id}",
    status_code=204,
    summary="초대장 삭제",
    description="""
    작가 본인이 생성한 초대장을 삭제합니다.
    
    - 본인 초대장만 삭제 가능 (권한 체크)
    - 삭제 시 관련된 방문 기록도 함께 삭제 (CASCADE)
    """,
)
async def delete_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    artist_uuid: str = Header(..., alias="X-Artist-UUID"),
):
    logger.info(f"초대장 삭제 시도: ID {invitation_id}, 작가 UUID {artist_uuid[:8]}...")

    # 작가 확인
    artist = db.query(Artist).filter(Artist.uuid == artist_uuid).first()
    if not artist:
        logger.warning(f"작가 UUID {artist_uuid[:8]}... 찾을 수 없음")
        raise HTTPException(status_code=401, detail="Invalid artist UUID")

    # 초대장 확인
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        logger.warning(f"초대장 ID {invitation_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Invitation not found")

    # 권한 확인
    if invitation.artist_id != artist.id:
        logger.warning(
            f"권한 없음: 초대장 ID {invitation_id}, 요청 작가 '{artist.name}', 소유 작가 ID {invitation.artist_id}"
        )
        raise HTTPException(status_code=403, detail="Not your invitation")

    # 실제 삭제
    invitation_code = invitation.code
    db.delete(invitation)
    db.commit()

    logger.info(
        f"✅ 초대장 삭제 완료: ID {invitation_id}, 코드 {invitation_code[:8]}..., 작가 '{artist.name}'"
    )

    return Response(status_code=204)


# ============================================================================
# 관객용 API (인증 불필요)
# ============================================================================


@router.get(
    "/code/{code}",
    response_model=InvitationPublicResponse,
    summary="초대장 조회 (관객용)",
    description="""
    초대장 코드로 초대장 상세 정보를 조회합니다.
    
    - 인증 불필요 (누구나 접근 가능)
    - 작가, 전시, 장소 정보 포함
    - 단순 조회는 view_count에 영향 없음 (실제 방문 시에만 증가)
    """,
)
async def get_invitation_by_code(code: str, db: Session = Depends(get_db)):
    logger.info(f"초대장 코드 조회: {code[:8]}...")

    # 초대장 조회
    invitation = db.query(Invitation).filter(Invitation.code == code).first()

    if not invitation:
        logger.warning(f"초대장 코드 {code[:8]}... 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Invitation not found")

    logger.info(f"✅ 초대장 조회 완료: 코드 {code[:8]}..., ID {invitation.id}")

    # Response 생성 (view_count 제외)
    return _build_invitation_public_response(invitation, db)


# ============================================================================
# Helper Functions
# ============================================================================


def _build_invitation_response(
    invitation: Invitation, db: Session
) -> InvitationResponse:
    """
    InvitationResponse 생성 헬퍼

    작가, 전시 정보를 포함한 완전한 응답 생성
    """
    # 작가 정보
    artist = db.query(Artist).filter(Artist.id == invitation.artist_id).first()
    artist_data = ArtistInInvitation(id=artist.id, name=artist.name, bio=artist.bio)

    # 전시 정보
    exhibition = (
        db.query(Exhibition).filter(Exhibition.id == invitation.exhibition_id).first()
    )
    venue_data = VenueInInvitation(
        name=exhibition.venue.name,
        address=exhibition.venue.address,
        geo_lat=exhibition.venue.geo_lat,
        geo_lon=exhibition.venue.geo_lon,
    )
    exhibition_data = ExhibitionInInvitation(
        id=exhibition.id,
        title=exhibition.title,
        description_text=exhibition.description_text,
        start_date=exhibition.start_date,
        end_date=exhibition.end_date,
        cover_image_url=exhibition.cover_image_url,
        venue=venue_data,
    )

    # Response
    return InvitationResponse(
        id=invitation.id,
        code=invitation.code,
        artist=artist_data,
        exhibition=exhibition_data,
        message=invitation.message,
        view_count=invitation.view_count,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
        deep_link=f"lastdance://invitation/{invitation.code}",
        app_store_link="https://apps.apple.com/kr/app/%EC%97%AC%EC%9A%B4/id6754415794",
    )


def _build_invitation_public_response(
    invitation: Invitation, db: Session
) -> InvitationPublicResponse:
    """
    InvitationPublicResponse 생성 헬퍼

    관객용 응답 (view_count 제외)
    """
    # 작가 정보
    artist = db.query(Artist).filter(Artist.id == invitation.artist_id).first()
    artist_data = ArtistInInvitation(id=artist.id, name=artist.name, bio=artist.bio)

    # 전시 정보
    exhibition = (
        db.query(Exhibition).filter(Exhibition.id == invitation.exhibition_id).first()
    )
    venue_data = VenueInInvitation(
        name=exhibition.venue.name,
        address=exhibition.venue.address,
        geo_lat=exhibition.venue.geo_lat,
        geo_lon=exhibition.venue.geo_lon,
    )
    exhibition_data = ExhibitionInInvitation(
        id=exhibition.id,
        title=exhibition.title,
        description_text=exhibition.description_text,
        start_date=exhibition.start_date,
        end_date=exhibition.end_date,
        cover_image_url=exhibition.cover_image_url,
        venue=venue_data,
    )

    # Response (view_count 제외)
    return InvitationPublicResponse(
        id=invitation.id,
        code=invitation.code,
        artist=artist_data,
        exhibition=exhibition_data,
        message=invitation.message,
        created_at=invitation.created_at,
    )


@router.post(
    "/interests",
    response_model=InvitationInterestResponse,
    status_code=201,
    summary="초대장 관심 표현 (갈게요)",
    description="""
    관객 또는 작가가 초대장을 보고 '갈게요' 버튼을 누를 때 호출합니다.
    
    - 한 사용자는 한 초대장에 한 번만 갈게요 가능
    - 중복 시도 시 409 에러 반환
    - 본인 전시는 갈게요 불가 (400 에러)
    - 성공 시 invitation.view_count 자동 증가
    """,
)
async def create_invitation_interest(
    data: InvitationInterestCreate,
    db: Session = Depends(get_db),
    user_uuid: str = Header(..., alias="X-User-UUID"),
):
    logger.info(
        f"초대장 관심 표현 시도: UUID {user_uuid[:8]}..., 초대장 ID {data.invitation_id}"
    )

    # 1. 초대장 확인
    invitation = (
        db.query(Invitation).filter(Invitation.id == data.invitation_id).first()
    )
    if not invitation:
        logger.warning(f"초대장 ID {data.invitation_id} 찾을 수 없음")
        raise HTTPException(status_code=404, detail="Invitation not found")

    # 2. Visitor 또는 Artist 확인
    visitor = db.query(Visitor).filter(Visitor.uuid == user_uuid).first()
    artist = db.query(Artist).filter(Artist.uuid == user_uuid).first()

    if not visitor and not artist:
        # 둘 다 없으면 Visitor 생성
        logger.info(f"신규 Visitor 생성: UUID {user_uuid[:8]}...")
        visitor = Visitor(uuid=user_uuid)
        db.add(visitor)
        db.flush()

    # 3. 본인 전시 체크 (Artist인 경우)
    if artist and invitation.artist_id == artist.id:
        logger.warning(
            f"본인 전시 관심 표현 시도: 작가 '{artist.name}', 초대장 ID {data.invitation_id}"
        )
        raise HTTPException(
            status_code=400, detail="본인의 전시에는 관심 표현을 할 수 없습니다."
        )

    # 4. 중복 체크
    existing = db.query(InvitationInterest).filter(
        InvitationInterest.invitation_id == data.invitation_id
    )

    if visitor:
        existing = existing.filter(InvitationInterest.visitor_id == visitor.id)
    elif artist:
        existing = existing.filter(InvitationInterest.artist_id == artist.id)

    if existing.first():
        user_type = "관람객" if visitor else "작가"
        logger.warning(
            f"중복 관심 표현 시도: {user_type}, 초대장 ID {data.invitation_id}"
        )
        raise HTTPException(
            status_code=409, detail="이미 이 초대장에 관심을 표현했습니다."
        )

    # 5. 관심 표현 생성
    interest = InvitationInterest(
        invitation_id=data.invitation_id,
        visitor_id=visitor.id if visitor else None,
        artist_id=artist.id if artist else None,
    )
    db.add(interest)

    # 6. view_count 증가
    old_count = invitation.view_count
    invitation.view_count += 1

    db.commit()
    db.refresh(interest)

    user_type = "관람객" if visitor else "작가"
    user_name = visitor.name if visitor else artist.name
    logger.info(
        f"✅ 관심 표현 완료: {user_type} '{user_name}', 초대장 ID {data.invitation_id}, "
        f"view_count {old_count} → {invitation.view_count}"
    )

    return interest
