# app/db/seed.py
from datetime import date
import logging

from app.db.session import SessionLocal
from app.models import (
    Artist,
    Artwork,
    Exhibition,
    Tag,
    TagCategory,
    Venue,
    Visitor,
    exhibition_artworks,
)
from app.models.reaction import Reaction, reaction_tags
from app.models.visit_history import VisitHistory

logger = logging.getLogger(__name__)


def seed_database():
    """가상의 전시 데이터로 데이터베이스 시딩"""
    db = SessionLocal()

    try:
        logger.info("데이터베이스 시딩 시작...")

        # 1. TagCategory 생성
        logger.info("태그 카테고리 생성 중...")
        categories = [
            TagCategory(name="감각", color_hex="#FF6B9D"),
            TagCategory(name="시간", color_hex="#4ECDC4"),
            TagCategory(name="공간", color_hex="#FFE66D"),
            TagCategory(name="질감", color_hex="#95E1D3"),
        ]
        db.add_all(categories)
        db.commit()
        logger.info(f"{len(categories)}개 카테고리 생성 완료")

        # 2. Tag 생성
        logger.info("태그 생성 중...")
        tags = [
            # 감각 (category_id=1)
            Tag(name="몽환적인", category_id=1, color_hex="#FF6B9D"),
            Tag(name="날카로운", category_id=1, color_hex="#FF6B9D"),
            Tag(name="부드러운", category_id=1, color_hex="#FF6B9D"),
            Tag(name="강렬한", category_id=1, color_hex="#FF6B9D"),
            Tag(name="고요한", category_id=1, color_hex="#FF6B9D"),
            # 시간 (category_id=2)
            Tag(name="영원한", category_id=2, color_hex="#4ECDC4"),
            Tag(name="순간적인", category_id=2, color_hex="#4ECDC4"),
            Tag(name="느린", category_id=2, color_hex="#4ECDC4"),
            Tag(name="빠른", category_id=2, color_hex="#4ECDC4"),
            Tag(name="정지된", category_id=2, color_hex="#4ECDC4"),
            # 공간 (category_id=3)
            Tag(name="넓은", category_id=3, color_hex="#FFE66D"),
            Tag(name="좁은", category_id=3, color_hex="#FFE66D"),
            Tag(name="깊은", category_id=3, color_hex="#FFE66D"),
            Tag(name="얕은", category_id=3, color_hex="#FFE66D"),
            Tag(name="무한한", category_id=3, color_hex="#FFE66D"),
            # 질감 (category_id=4)
            Tag(name="매끄러운", category_id=4, color_hex="#95E1D3"),
            Tag(name="거친", category_id=4, color_hex="#95E1D3"),
            Tag(name="투명한", category_id=4, color_hex="#95E1D3"),
            Tag(name="불투명한", category_id=4, color_hex="#95E1D3"),
            Tag(name="흐릿한", category_id=4, color_hex="#95E1D3"),
        ]
        db.add_all(tags)
        db.commit()
        logger.info(f"{len(tags)}개 태그 생성 완료")

        # 3. Venue 생성
        logger.info("전시 장소 생성 중...")
        venues = [
            Venue(
                name="루미나 갤러리",
                address="서울특별시 종로구 빛의거리 42",
                geo_lat=37.5799,
                geo_lon=126.9770,
            ),
            Venue(
                name="에테르 아트홀",
                address="서울특별시 강남구 공간로 128",
                geo_lat=37.5172,
                geo_lon=127.0473,
            ),
            Venue(
                name="크로노스 미술관",
                address="서울특별시 용산구 시간의길 7",
                geo_lat=37.5326,
                geo_lon=126.9900,
            ),
        ]
        db.add_all(venues)
        db.commit()
        logger.info(f"{len(venues)}개 장소 생성 완료")

        # 4. Artist 생성
        logger.info("작가 생성 중...")
        artists = [
            Artist(
                name="나비야",
                bio="빛과 그림자를 탐구하는 설치 작가. 공간의 본질을 재해석한다.",
                email="naviya@artmail.com",
            ),
            Artist(
                name="린 카이",
                bio="시간의 흐름을 시각화하는 영상 작가. 순간과 영원 사이를 넘나든다.",
                email="lin.kai@artmail.com",
            ),
            Artist(
                name="제로 문",
                bio="무의식의 풍경을 그리는 화가. 꿈과 현실의 경계를 허문다.",
                email="zero.moon@artmail.com",
            ),
            Artist(
                name="소라 진",
                bio="소리를 조각하는 사운드 아티스트. 침묵 속에서 울림을 찾는다.",
                email="sora.jin@artmail.com",
            ),
            Artist(
                name="아리스",
                bio="감정의 색채를 담는 미디어 아티스트. 마음의 스펙트럼을 표현한다.",
                email="aris@artmail.com",
            ),
        ]
        db.add_all(artists)
        db.commit()
        logger.info(f"{len(artists)}개 작가 생성 완료")

        # 5. Exhibition 생성
        logger.info("전시 생성 중...")
        exhibitions = [
            Exhibition(
                title="테스트 전시1",
                description_text="빛과 어둠이 만나는 지점에서 기억을 소환하다. 잊혀진 순간들이 빛을 통해 되살아나는 감각적 여정.",
                start_date=date(2025, 9, 1),
                end_date=date(2025, 11, 30),
                venue_id=venues[0].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/exhibitions/47001042-2663-4ae8-8f5e-6ec9a5180a44.jpg",
            ),
            Exhibition(
                title="테스트 전시2",
                description_text="흩어진 시간의 조각들을 모아 새로운 우주를 구축하다. 과거와 미래가 현재에서 만나는 시공간적 실험.",
                start_date=date(2025, 10, 1),
                end_date=date(2025, 12, 31),
                venue_id=venues[1].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/exhibitions/615bfa98-298e-4803-9ba3-d3749e622618.jpg",
            ),
            Exhibition(
                title="테스트 전시3",
                description_text="잠든 마음 속 정원을 거닐다. 의식 너머 펼쳐진 내면의 풍경을 시각적으로 탐험하는 초현실적 전시.",
                start_date=date(2025, 8, 15),
                end_date=date(2025, 10, 31),
                venue_id=venues[2].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/exhibitions/3942a480-79e9-4924-be29-de928ce86464.jpg",
            ),
        ]
        db.add_all(exhibitions)
        db.commit()
        logger.info(f"{len(exhibitions)}개 전시 생성 완료")

        # 6. Artwork 생성
        logger.info("작품 생성 중...")
        artworks = [
            # 빛의 기억 전시 작품들
            Artwork(
                title="새벽의 속삭임",
                artist_id=artists[0].id,
                description="빛이 어둠을 깨우는 순간, 하루가 시작되기 전 고요한 대화",
                year=2024,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/fe86362a-2b35-4fbe-b164-5540456e8968.jpg",
            ),
            Artwork(
                title="잊혀진 파장",
                artist_id=artists[0].id,
                description="기억 속에 남은 빛의 떨림, 시간이 남긴 흔적",
                year=2024,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/85126327-3c80-45c4-9f2d-f33605068b57.jpg",
            ),
            Artwork(
                title="투명한 메아리",
                artist_id=artists[1].id,
                description="빛이 공간을 통과하며 남긴 소리 없는 울림",
                year=2023,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/4407ec8e-6a88-4092-b618-c67d4d847fc6.jpg",
            ),
            # 시간의 파편 전시 작품들
            Artwork(
                title="정지된 흐름",
                artist_id=artists[1].id,
                description="멈춘 듯 흐르는 시간, 역설의 시각화",
                year=2024,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/f0218c11-a23d-4602-8397-1628b06d5dce.jpg",
            ),
            Artwork(
                title="순간의 무게",
                artist_id=artists[2].id,
                description="찰나가 품은 영원함, 시간의 밀도를 느끼다",
                year=2024,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/622d47dd-4ebd-4d47-bfc3-833181bfa6e7.jpg",
            ),
            Artwork(
                title="과거의 미래",
                artist_id=artists[2].id,
                description="지나간 시간이 예견한 다가올 세계",
                year=2023,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/artworks/c2d12ea5-d14b-449a-99b6-cb501356fac4.jpg",
            ),
        ]
        db.add_all(artworks)
        db.commit()
        logger.info(f"{len(artworks)}개 작품 생성 완료")

        # 7. Exhibition-Artwork M:N 관계 설정
        logger.info("전시-작품 연결 중...")
        # 빛의 기억: 작품 0, 1, 2
        db.execute(
            exhibition_artworks.insert().values(
                [
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[0].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[1].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[2].id},
                ]
            )
        )

        # 시간의 파편: 작품 3, 4, 5
        db.execute(
            exhibition_artworks.insert().values(
                [
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[3].id},
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[4].id},
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[5].id},
                ]
            )
        )

        # 무의식의 정원: 작품 연결 없음 (주석 처리)
        # db.execute(
        #     exhibition_artworks.insert().values([
        #         {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[6].id},
        #         {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[7].id},
        #         {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[8].id},
        #         {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[9].id}
        #     ])
        # )
        db.commit()
        logger.info("작품 연결 완료")

        # 8. Visitor 생성
        logger.info("관람객 생성 중...")
        visitors = [
            Visitor(uuid="visitor-alpha-001", name="알파"),
            Visitor(uuid="visitor-beta-002", name="베타"),
            Visitor(uuid="visitor-gamma-003", name="감마"),
            Visitor(uuid="visitor-delta-004", name="델타"),
            Visitor(uuid="visitor-epsilon-005", name="엡실론"),
        ]
        db.add_all(visitors)
        db.commit()
        logger.info(f"{len(visitors)}명 관람객 생성 완료")

        # 9. VisitHistory 생성 (알파가 전시1 관람)
        logger.info("방문 기록 생성 중...")
        visit = VisitHistory(
            visitor_id=visitors[0].id,  # 알파
            exhibition_id=exhibitions[0].id,  # 테스트 전시1
        )
        db.add(visit)
        db.commit()
        logger.info("알파 방문 기록 생성 완료")

        # 10. Reaction 생성 (알파가 작품1에 반응)
        logger.info("반응 생성 중...")
        reaction = Reaction(
            artwork_id=artworks[0].id,  # 새벽의 속삭임
            visitor_id=visitors[0].id,  # 알파
            visit_id=visit.id,
            comment="빛과 어둠의 경계가 주는 고요함이 마음을 울렸어요. 새벽의 감성이 느껴지는 작품이네요.",
        )
        db.add(reaction)
        db.commit()

        # 반응에 태그 추가
        db.execute(
            reaction_tags.insert().values(
                [
                    {"reaction_id": reaction.id, "tag_id": tags[0].id},  # 몽환적인
                    {"reaction_id": reaction.id, "tag_id": tags[4].id},  # 고요한
                ]
            )
        )
        db.commit()
        logger.info("알파 태그 포함 반응 생성 완료")

        logger.info("\n데이터베이스 시딩 완료!")
        logger.info(
            f"""
        요약:
        - {len(categories)}개 태그 카테고리
        - {len(tags)}개 태그
        - {len(venues)}개 장소
        - {len(artists)}명 작가
        - {len(exhibitions)}개 전시
        - {len(artworks)}개 작품
        - {len(visitors)}명 관람객
        - 1개 방문 기록
        - 2개 태그 포함 1개 반응
        """
        )

    except Exception as e:
        logger.error(f"\n시딩 중 에러 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
