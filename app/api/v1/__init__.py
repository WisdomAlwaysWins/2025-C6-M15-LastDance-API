from fastapi import APIRouter
from app.api.v1.endpoints import admin, users, exhibitions, artworks, reviews, visits

api_router = APIRouter()

# 라우터 등록
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(exhibitions.router, prefix="/exhibitions", tags=["Exhibitions"])
api_router.include_router(artworks.router, prefix="/artworks", tags=["Artworks"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(visits.router, prefix="/visits", tags=["Visits"])