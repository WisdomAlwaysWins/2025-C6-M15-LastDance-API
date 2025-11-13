# app/api/v1/api.py (또는 app/main.py)
from app.api.v1.endpoints import (
    artists,
    artworks,
    device,
    exhibitions,
    reactions,
    tag_categories,
    tags,
    upload,
    venues,
    visit_histories,
    visitors,
)
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(artists.router)
api_router.include_router(artworks.router)
api_router.include_router(exhibitions.router)
api_router.include_router(reactions.router)
api_router.include_router(tag_categories.router)
api_router.include_router(tags.router)
api_router.include_router(venues.router)
api_router.include_router(visit_histories.router)
api_router.include_router(visitors.router)
api_router.include_router(device.router)
api_router.include_router(upload.router)
