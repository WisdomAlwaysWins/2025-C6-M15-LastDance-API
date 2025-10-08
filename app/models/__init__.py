"""
모든 모델을 한 곳에서 임포트
Alembic이 모델을 인식하려면 반드시 필요!
"""
from app.models.user import User, UserType
from app.models.exhibition import Exhibition
from app.models.artwork import Artwork
from app.models.tag import Tag
from app.models.review import Review, review_tags
from app.models.visit_history import VisitHistory

__all__ = [
    "User",
    "UserType",
    "Exhibition",
    "Artwork",
    "Tag",
    "Review",
    "review_tags",
    "VisitHistory",
]