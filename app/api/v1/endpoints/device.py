import logging

from sqlalchemy.orm import Session

# from app.api.deps import verify_api_key
from app.database import get_db
from app.models.artist import Artist
from app.models.device import Device
from app.models.visitor import Visitor
from app.schemas.device import (
    DeviceResponse,
    DeviceTokenRegister,
    DeviceUpdate,
    NotificationSendRequest,
)
from app.utils.apns_client import get_apns_client
from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post(
    "/register-token",
    response_model=dict,
    summary="디바이스 토큰 등록",
    description="iOS 앱에서 받은 APNs 디바이스 토큰을 서버에 등록합니다. 관람객 또는 작가 계정에 연결됩니다.",
)
def register_device_token(data: DeviceTokenRegister, db: Session = Depends(get_db)):
    """
    디바이스 토큰 등록

    iOS 앱에서 APNs 토큰을 받으면 이 API를 호출하여 서버에 저장합니다.
    visitor_id 또는 artist_id 중 하나는 필수입니다.

    Args:
        data: 디바이스 토큰 등록 정보 (validator에서 검증)

    Returns:
        dict: 등록 결과 메시지

    Raises:
        404: 존재하지 않는 visitor_id 또는 artist_id
    """

    # Visitor 존재 여부 확인
    if data.visitor_id:
        visitor = db.query(Visitor).filter(Visitor.id == data.visitor_id).first()
        if not visitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"관람객 ID {data.visitor_id}를 찾을 수 없습니다",
            )

    # Artist 존재 여부 확인
    if data.artist_id:
        artist = db.query(Artist).filter(Artist.id == data.artist_id).first()
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {data.artist_id}를 찾을 수 없습니다",
            )

    # 기존 토큰 확인
    existing = (
        db.query(Device).filter(Device.device_token == data.device_token).first()
    )

    if existing:
        # visitor_id, artist_id 업데이트
        existing.visitor_id = data.visitor_id
        existing.artist_id = data.artist_id
        existing.is_active = True  # Boolean
        db.commit()
        
        user_type = "관람객" if data.visitor_id else "작가"
        user_id = data.visitor_id or data.artist_id
        logger.info(
            f"디바이스 토큰 업데이트: {data.device_token[:10]}... → {user_type} {user_id}"
        )
        return {"message": "디바이스 토큰 업데이트 완료"}

    # 신규 등록
    device = Device(
        visitor_id=data.visitor_id,
        artist_id=data.artist_id,
        device_token=data.device_token,
        is_active=True,  # Boolean
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    user_type = "관람객" if data.visitor_id else "작가"
    user_id = data.visitor_id or data.artist_id
    logger.info(
        f"디바이스 토큰 등록: {data.device_token[:10]}... → {user_type} {user_id}"
    )
    return {"message": "디바이스 토큰 등록 완료", "device_id": device.id}


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="디바이스 상태 변경",
    description="디바이스 활성/비활성 상태를 변경합니다.",
)
def update_device(
    device_id: int,
    device_data: DeviceUpdate, 
    db: Session = Depends(get_db),
):
    """
    디바이스 활성/비활성 상태 변경

    Args:
        device_id: 디바이스 ID
        device_data: 수정할 데이터

    Returns:
        DeviceResponse: 수정된 디바이스 정보

    Raises:
        404: 존재하지 않는 디바이스
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="디바이스를 찾을 수 없습니다"
        )
    
    device.is_active = device_data.is_active
    db.commit()
    db.refresh(device)
    
    logger.info(
        f"디바이스 상태 변경: ID {device_id} → {'활성' if device.is_active else '비활성'}"
    )
    
    return device


@router.delete(
    "/unregister-token/{device_token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="디바이스 토큰 삭제",
    description="디바이스 토큰을 비활성화합니다.",
)
def unregister_device_token(device_token: str, db: Session = Depends(get_db)):
    """
    디바이스 토큰 비활성화

    로그아웃 또는 앱 삭제 시 호출하여 푸시 알림을 받지 않도록 합니다.

    Args:
        device_token: 비활성화할 디바이스 토큰

    Raises:
        404: 존재하지 않는 디바이스 토큰
    """
    device = db.query(Device).filter(Device.device_token == device_token).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="디바이스 토큰을 찾을 수 없습니다",
        )

    device.is_active = False
    db.commit()

    logger.info(f"디바이스 토큰 비활성화: {device_token[:10]}...")
    return None


@router.get(
    "/visitor/{visitor_id}",
    response_model=list[DeviceResponse],
    summary="관람객 디바이스 목록 조회",
    description="특정 관람객의 등록된 디바이스 목록을 조회합니다.",
)
def get_visitor_devices(
    visitor_id: int,
    db: Session = Depends(get_db),
    # _: bool = Depends(verify_api_key),
):
    """
    관람객 디바이스 목록 조회 (관리자)

    Args:
        visitor_id: 관람객 ID

    Returns:
        list[DeviceResponse]: 디바이스 목록

    Raises:
        404: 존재하지 않는 관람객
    """
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"관람객 ID {visitor_id}를 찾을 수 없습니다",
        )

    devices = (
        db.query(Device)
        .filter(Device.visitor_id == visitor_id, Device.is_active == True)
        .all()
    )

    return devices


@router.get(
    "/artist/{artist_id}",
    response_model=list[DeviceResponse],
    summary="작가 디바이스 목록 조회",
    description="특정 작가의 등록된 디바이스 목록을 조회합니다.",
)
def get_artist_devices(
    artist_id: int,
    db: Session = Depends(get_db),
    # _: bool = Depends(verify_api_key),
):
    """
    작가 디바이스 목록 조회 (관리자)

    Args:
        artist_id: 작가 ID

    Returns:
        list[DeviceResponse]: 디바이스 목록

    Raises:
        404: 존재하지 않는 작가
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작가 ID {artist_id}를 찾을 수 없습니다",
        )

    devices = (
        db.query(Device)
        .filter(Device.artist_id == artist_id, Device.is_active == True)
        .all()
    )

    return devices


@router.post(
    "/send-notification",
    summary="푸시 알림 전송 (테스트)",
    description="특정 사용자 또는 디바이스에 푸시 알림을 전송합니다. (관리자 전용)",
)
async def send_push_notification(
    request: NotificationSendRequest,
    db: Session = Depends(get_db),
    # _: bool = Depends(verify_api_key),
):
    """
    푸시 알림 전송 (관리자 테스트용)

    visitor_id, artist_id, device_token 중 하나는 필수입니다.

    Args:
        request: 푸시 알림 전송 요청 (validator에서 검증)

    Returns:
        dict: 전송 결과

    Raises:
        404: 등록된 디바이스 없음
    """

    apns = get_apns_client(use_sandbox=request.use_sandbox)
    device_tokens = []

    # visitor_id로 전송
    if request.visitor_id:
        devices = (
            db.query(Device)
            .filter(
                Device.visitor_id == request.visitor_id,
                Device.is_active == True,
            )
            .all()
        )

        if not devices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"관람객 ID {request.visitor_id}의 활성 디바이스가 없습니다",
            )

        device_tokens = [device.device_token for device in devices]

    # artist_id로 전송
    elif request.artist_id:
        devices = (
            db.query(Device)
            .filter(
                Device.artist_id == request.artist_id,
                Device.is_active == True,
            )
            .all()
        )

        if not devices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작가 ID {request.artist_id}의 활성 디바이스가 없습니다",
            )

        device_tokens = [device.device_token for device in devices]

    # device_token으로 전송
    elif request.device_token:
        device_tokens = [request.device_token]

    # 푸시 전송
    try:
        result = await apns.send_batch_notification(
            device_tokens=device_tokens,
            title=request.title,
            body=request.body,
            data=request.data,
            badge=request.badge,
        )

        env = "Sandbox" if request.use_sandbox else "Production"
        logger.info(
            f"[{env}] 푸시 전송 완료: 성공 {result['success']}개, 실패 {result['failed']}개"
        )

        return {
            "message": f"{len(device_tokens)}개 디바이스에 전송 요청 완료",
            "environment": env,
            "success_count": result["success"],
            "failed_count": result["failed"],
        }

    except Exception as e:
        logger.error(f"푸시 전송 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"푸시 전송 중 오류 발생: {str(e)}",
        )