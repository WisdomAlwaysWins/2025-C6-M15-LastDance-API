# 🎨 LastDance API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

> 전시 관람 경험을 기록하고 공유하는 플랫폼 - iOS 앱을 위한 RESTful API

---

## 📋 목차

- [✨ 주요 기능](#-주요-기능)
- [🛠 기술 스택](#-기술-스택)
- [🚀 빠른 시작](#-빠른-시작)
- [📡 API 엔드포인트](#-api-엔드포인트)
- [🗂 프로젝트 구조](#-프로젝트-구조)
- [🔐 환경 변수](#-환경-변수)
- [📝 Git Convention](#-git-convention)

---

## ✨ 주요 기능

### 👥 관람객 (Visitor)
- **전시 탐색**: 진행 중/예정/종료된 전시 조회
- **작품 감상**: 작품 정보 및 작가 정보 확인
- **감정 태그**: 작품에 대한 감정 표현 (몽환적인, 고요한 등)
- **리뷰 작성**: 자유로운 감상평 작성
- **관람 이력**: 방문한 전시와 평가한 작품 아카이빙

### 🎭 작가 (Artist)
- **작품 관리**: 자신의 작품 목록 조회
- **전시 참여**: 참여한 전시 정보 확인
- **반응 확인**: 관람객들의 평가 및 리뷰 조회

### 🏛️ 관리자 (Admin)
- **전시 관리**: 전시 등록, 수정, 삭제
- **작품 관리**: 작품 정보 및 썸네일 관리
- **장소 관리**: 전시 장소 등록 및 관리
- **태그 시스템**: 감정 태그 카테고리 및 태그 관리
- **이미지 업로드**: AWS S3 연동 이미지 관리

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
- **Validation**: Pydantic v2
- **AWS SDK**: boto3

---

## 🚀 빠른 시작

### Prerequisites
- Docker & Docker Compose
- AWS S3 Bucket (이미지 업로드용)
- PostgreSQL 14+ (로컬 개발 시)

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/2025-C6-M15-LastDance-API.git
cd 2025-C6-M15-LastDance-API
```

### 2. 환경 변수 설정
`.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일 수정:
```bash
# Database
DATABASE_URL=postgresql://lastdance:password@db:5432/lastdance
POSTGRES_USER=lastdance
POSTGRES_PASSWORD=your-password
POSTGRES_DB=lastdance

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=your-bucket-name

# Application
API_V1_PREFIX=/api/v1
PROJECT_NAME=LastDance API
```

### 3. Docker로 실행
```bash
# 컨테이너 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f api

# DB 마이그레이션
docker-compose exec api alembic upgrade head

# 시딩 데이터 생성 (테스트용)
docker-compose exec api python -m app.db.seed
```

### 4. API 접속
- **API 문서**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API 엔드포인트

### 🏛️ Exhibitions (전시)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/exhibitions` | 전시 목록 조회 (status 필터링 가능) |
| `GET` | `/api/v1/exhibitions/{id}` | 전시 상세 조회 (장소, 작품 포함) |
| `POST` | `/api/v1/exhibitions` | 전시 생성 (관리자) |
| `PUT` | `/api/v1/exhibitions/{id}` | 전시 수정 (관리자) |
| `DELETE` | `/api/v1/exhibitions/{id}` | 전시 삭제 (관리자) |

### 🖼️ Artworks (작품)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/artworks` | 작품 목록 조회 |
| `GET` | `/api/v1/artworks/{id}` | 작품 상세 조회 (작가, 전시 포함) |
| `POST` | `/api/v1/artworks` | 작품 생성 (관리자) |
| `PUT` | `/api/v1/artworks/{id}` | 작품 수정 (관리자) |
| `DELETE` | `/api/v1/artworks/{id}` | 작품 삭제 (관리자) |

### 🎭 Artists (작가)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/artists` | 작가 목록 조회 |
| `GET` | `/api/v1/artists/{id}` | 작가 상세 조회 |
| `GET` | `/api/v1/artists/uuid/{uuid}` | 작가 UUID로 조회 |

### 💬 Reactions (반응/평가)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/reactions` | 반응 목록 조회 (필터링 가능) |
| `GET` | `/api/v1/reactions/{id}` | 반응 상세 조회 |
| `POST` | `/api/v1/reactions` | 반응 생성 (태그, 코멘트) |
| `PUT` | `/api/v1/reactions/{id}` | 반응 수정 |
| `DELETE` | `/api/v1/reactions/{id}` | 반응 삭제 |

### 🏷️ Tags (태그)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/tag-categories` | 태그 카테고리 목록 |
| `GET` | `/api/v1/tag-categories/{id}` | 카테고리 상세 (태그 포함) |
| `GET` | `/api/v1/tags` | 태그 목록 조회 |
| `GET` | `/api/v1/tags/{id}` | 태그 상세 조회 |

### 👤 Visitors (관람객)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/visitors` | 관람객 목록 (관리자) |
| `GET` | `/api/v1/visitors/{id}` | 관람객 정보 조회 |
| `GET` | `/api/v1/visitors/uuid/{uuid}` | UUID로 관람객 조회 |
| `POST` | `/api/v1/visitors` | 관람객 등록 |

### 📤 Upload (이미지 업로드)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | 일반 이미지 업로드 |
| `POST` | `/api/v1/upload/exhibition` | 전시 포스터 업로드 |
| `POST` | `/api/v1/upload/artwork` | 작품 썸네일 업로드 |

**자세한 API 문서**: http://52.78.41.179:8000/docs

---

## 🗂 프로젝트 구조

```
2025-C6-M15-LastDance-API/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── artists.py        # 작가 API
│   │       ├── artworks.py       # 작품 API
│   │       ├── exhibitions.py    # 전시 API
│   │       ├── reactions.py      # 반응/평가 API
│   │       ├── tags.py           # 태그 API
│   │       ├── visitors.py       # 관람객 API
│   │       ├── venues.py         # 장소 API
│   │       └── upload.py         # 이미지 업로드 API
│   ├── models/                   # SQLAlchemy 모델
│   │   ├── artist.py
│   │   ├── artwork.py
│   │   ├── exhibition.py
│   │   ├── reaction.py
│   │   ├── tag.py
│   │   ├── tag_category.py
│   │   ├── venue.py
│   │   ├── visitor.py
│   │   └── visit_history.py
│   ├── schemas/                  # Pydantic 스키마
│   ├── services/                 # 비즈니스 로직
│   ├── db/
│   │   ├── session.py            # DB 세션
│   │   └── seed.py               # 시딩 데이터
│   ├── config.py                 # 설정
│   ├── database.py               # DB 연결
│   └── main.py                   # FastAPI 앱
├── alembic/                      # 마이그레이션
├── docker-compose.yml            # Docker 설정
├── Dockerfile                    # Docker 이미지
├── requirements.txt              # Python 패키지
└── README.md
```

---

## 🔐 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL 연결 URL | `postgresql://user:pass@host:5432/db` |
| `POSTGRES_USER` | DB 사용자명 | `lastdance` |
| `POSTGRES_PASSWORD` | DB 비밀번호 | `your-password` |
| `POSTGRES_DB` | DB 이름 | `lastdance` |
| `AWS_ACCESS_KEY_ID` | AWS 액세스 키 | `AKIAXXXXXXXX` |
| `AWS_SECRET_ACCESS_KEY` | AWS 시크릿 키 | `xxxxxx` |
| `AWS_REGION` | AWS 리전 | `ap-northeast-2` |
| `S3_BUCKET_NAME` | S3 버킷 이름 | `lastdance-bucket` |

---

## 📝 Git Convention

### 브랜치 전략
```
feature/#이슈번호/기능명
```

**예시**: `feature/#13/exhibition-api`

### 커밋 메시지
```
깃모지 [태그] #이슈번호 설명
```

**예시**: `✨ [feat] #13 전시 API 구현`

#### 깃모지 태그
| 이모지 | 태그 | 설명 |
|--------|------|------|
| ✨ | `feat` | 새로운 기능 추가 |
| 🐛 | `fix` | 버그 수정 |
| ✅ | `chore` | 자잘한 수정 |
| 🗃️ | `DB` | 데이터베이스 관련 |
| 📝 | `docs` | 문서 작성/수정 |
| ♻️ | `refactor` | 리팩토링 |
| 🚧 | `setting` | 기본 설정 |

---

## 🌐 배포

### Production
- **서버**: AWS EC2 (Ubuntu 22.04)
- **주소**: http://52.78.41.179:8000
- **Swagger**: http://52.78.41.179:8000/docs

### 배포 프로세스
```bash
# 1. 코드 푸시
git push origin release/v1.0.0

# 2. EC2 접속
ssh -i key.pem ubuntu@52.78.41.179

# 3. 코드 업데이트
cd 2025-C6-M15-LastDance-API
git pull origin release/v1.0.0

# 4. 재배포
sudo docker-compose down
sudo docker-compose up -d --build
```
