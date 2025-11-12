# app/schemas/device.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DeviceTokenRegister(BaseModel):
    """
    디바이스 토큰 등록 요청

    Attributes:
        visitor_id: 관람객 ID (선택)
        artist_id: 작가 ID (선택)
        device_token: APNs 디바이스 토큰

    Note:
        visitor_id와 artist_id 중 하나는 필수
    """

    visitor_id: Optional[int] = Field(None, description="관람객 ID")
    artist_id: Optional[int] = Field(None, description="작가 ID")
    device_token: str = Field(..., description="APNs 디바이스 토큰")

    @model_validator(mode="after")
    def check_at_least_one_id(self):
        """visitor_id와 artist_id 중 하나는 필수"""
        if self.visitor_id is None and self.artist_id is None:
            raise ValueError("visitor_id 또는 artist_id 중 하나는 필수입니다")
        return self


class DeviceResponse(BaseModel):
    """
    디바이스 정보 응답

    Attributes:
        id: 디바이스 ID
        visitor_id: 관람객 ID
        artist_id: 작가 ID
        device_token: APNs 디바이스 토큰
        is_active: 활성 상태
        created_at: 등록 일시
        updated_at: 수정 일시
    """

    id: int
    visitor_id: Optional[int] = None
    artist_id: Optional[int] = None
    device_token: str
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceUpdate(BaseModel):
    """
    디바이스 수정 요청

    Attributes:
        is_active: 활성 상태
    """
    
    is_active: bool = Field(..., description="활성 상태 (True: 활성, False: 비활성)")


class NotificationSendRequest(BaseModel):
    """
    푸시 알림 전송 요청

    Attributes:
        visitor_id: 대상 관람객 ID (선택)
        artist_id: 대상 작가 ID (선택)
        device_token: 대상 디바이스 토큰 (선택)
        title: 알림 제목
        body: 알림 내용
        data: 추가 데이터 (선택)
        badge: 뱃지 숫자 (선택)
        use_sandbox: Sandbox 사용 여부 (기본값: True)

    Note:
        visitor_id, artist_id, device_token 중 하나는 필수
    """

    visitor_id: Optional[int] = Field(None, description="대상 관람객 ID")
    artist_id: Optional[int] = Field(None, description="대상 작가 ID")
    device_token: Optional[str] = Field(None, description="대상 디바이스 토큰")
    title: str = Field(..., description="알림 제목")
    body: str = Field(..., description="알림 내용")
    data: Optional[dict] = Field(None, description="추가 데이터")
    badge: Optional[int] = Field(None, description="뱃지 숫자")
    use_sandbox: bool = Field(True, description="Sandbox 사용 여부")

    @model_validator(mode="after")
    def check_at_least_one_target(self):
        """visitor_id, artist_id, device_token 중 하나는 필수"""
        if not any([self.visitor_id, self.artist_id, self.device_token]):
            raise ValueError("visitor_id, artist_id, device_token 중 하나는 필수입니다")
        return self