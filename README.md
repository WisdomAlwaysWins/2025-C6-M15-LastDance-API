# 🎨 LastDance API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

---

## 📋 목차

- [✨ 주요 기능](#-주요-기능)
- [🛠 기술 스택](#-기술-스택)
- [🚀 빠른 시작](#-빠른-시작)
- [📡 API 문서](#-api-문서)
- [🗂 프로젝트 구조](#-프로젝트-구조)
- [🐳 배포](#-배포)
- [📝 개발 가이드](#-개발-가이드)

---

## ✨ 주요 기능

### 관람객
- 🖼️ **작품 촬영 및 식별**: 사진으로 작품 정보 자동 인식 (Phase 2)
- 💭 **감정 태그 평가**: 시원해요, 슬퍼요 등 감정 태그 선택
- ✍️ **텍스트 리뷰**: 자유로운 감상 작성
- 📚 **관람 이력**: 방문한 전시와 평가한 작품 아카이빙

### 작가
- 🎭 **참여 전시**: 자신이 참여한 전시 목록 조회
- 💬 **관람객 반응**: 실시간 반응 확인

### 관리자
- 🏛️ **전시 관리**: 전시 등록, 수정, 포스터 업로드
- 🖼️ **작품 관리**: 작품 정보 및 이미지 관리 (AWS S3)
- 🏷️ **태그 관리**: 감정 태그 등록

---

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI 0.115.0
- **Language**: Python 3.12
- **Database**: PostgreSQL 14
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic

### Infrastructure
- **Storage**: AWS S3 (이미지 스토리지)
- **Deployment**: Docker, Docker Compose
- **Server**: AWS EC2 (Ubuntu 22.04)

### Libraries
- **Image Processing**: Pillow
- **File Upload**: python-multipart
- **Validation**: Pydantic
- **AWS SDK**: boto3

---

## 🚀 빠른 시작

### Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Docker & Docker Compose
- AWS S3 Bucket

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/2025-C6-M15-LastDance-API.git
cd 2025-C6-M15-LastDance-API
```

### 2. 환경 변수 설정
`.env` 파일은 공유할 수 없습니다 (단호)
```bash
cp .env.example env
```

### 3. Docker로 실행
도커는 알아서 잘 설치하실거라고 믿습니다.
```bash
docker-compose up -d --build
```

### 4. 로컬 개발 환경 구성
로컬 서버에서 실행하고 싶으시다면 다음과 같은 과정을 거쳐야합니다.
```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate # MacOS 기준

# 패키지 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### 5. 접속 확인

- API : http://localhost:8000
- Swagger UI : http://localhost:8000/docs
- Health Check : http://localhost:8000/health

---

## 📡 API 문서

Swagger UI를 통해서 모든 API 엔드포인트를 확인하고 직접 테스트할 수 있습니다.

### 주요 엔드 포인트

|카테고리|메서드|엔드포인트|설명|
|---|---|---|---|
|User|POST|`/api/v1/users`|사용자 설명|
|Exhibition|GET|`/api/v1/exhibitions`|전시목록|
|Artwork|GET|`/api/v1/artworks/{id}`|작품 상세|
|Review|POST|`/api/v1/reviews/`|평가 등록|
|Visit|POST|`/api/v1/visits/`|전시 방문기록|
|Artist|GET|`/api/v1/artists/exhibitions/`|작가 전시 목록|
|Admin|POST|`/api/v1/admin/artworks/`|작품 등록|

---

## 🗂️ 프로젝트 구조
```
2025-C6-M15-LastDance-API/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/        # API 엔드포인트
│   │           ├── admin.py      # 관리자 API
│   │           ├── users.py      # 사용자 API
│   │           ├── exhibitions.py
│   │           ├── artworks.py
│   │           ├── reviews.py
│   │           ├── visits.py
│   │           └── artists.py
│   ├── core/                     # 핵심 기능
│   │   └── (CLIP 모델 예정)
│   ├── models/                   # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── exhibition.py
│   │   ├── artwork.py
│   │   ├── tag.py
│   │   ├── review.py
│   │   └── visit_history.py
│   ├── schemas/                  # Pydantic 스키마
│   ├── utils/
│   │   └── s3_client.py         # AWS S3 클라이언트
│   ├── config.py                 # 환경 설정
│   ├── database.py               # DB 연결
│   └── main.py                   # 진입점
├── alembic/                      # 마이그레이션
├── tests/                        # 테스트 (TODO)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
