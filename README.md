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
- **작품 감상**: 작품 촬영 및 AI 기반 작품 매칭
- **감정 태그**: 작품에 대한 감정 표현 (최대 3개)
- **반응 기록**: 작품 사진과 함께 감상 기록 남기기
- **관람 이력**: 방문한 전시와 반응한 작품 아카이빙
- **푸시 알림**: 작가의 답글 알림 수신

### 🎭 작가 (Artist)

- **6자 코드 로그인**: 숫자+영문+특수문자 조합 코드로 간편 인증
- **작품 관리**: 자신의 작품 목록 조회
- **전시 참여**: 참여한 전시 정보 확인
- **반응 확인**: 관람객들의 반응 및 사진 조회
- **이모지 답글**: 관람객 반응에 5가지 이모지로 답변 (반응당 1개)
- **메시지 답글**: 관람객에게 짧은 메시지 전송 (10자 이내, 여러 번 가능)
- **푸시 알림**: 새로운 반응 알림 수신

### 🏛️ 관리자 (Admin)

- **전시 관리**: 전시 등록, 수정, 삭제
- **작품 관리**: 작품 정보 및 썸네일 관리, AI 임베딩 생성
- **작가 관리**: 작가 등록 및 로그인 코드 생성
- **장소 관리**: 전시 장소 등록 및 관리
- **태그 시스템**: 감정 태그 카테고리 및 태그 관리
- **이미지 업로드**: AWS S3 연동 이미지 관리
- **디바이스 관리**: 푸시 알림 테스트 및 관리

---

## 🛠 기술 스택

### Backend

- **Framework**: FastAPI 0.115.0
- **Language**: Python 3.12
- **Database**: PostgreSQL 14 + pgvector
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic

### Infrastructure

- **Storage**: AWS S3 (이미지 스토리지)
- **AI/ML**: AWS Lambda + DINOv2 (작품 이미지 매칭)
- **Push**: APNs (iOS 푸시 알림)
- **Deployment**: Docker, Docker Compose
- **Server**: AWS EC2 (Ubuntu 22.04)

### Libraries

- **Image Processing**: Pillow
- **File Upload**: python-multipart
- **Validation**: Pydantic v2
- **AWS SDK**: boto3
- **Push Notification**: aioapns
