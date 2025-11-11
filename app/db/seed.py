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
    """인상주의 화가들의 작품 전시 데이터로 데이터베이스 시딩"""
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
                name="국립현대미술관 서울관",
                address="서울특별시 종로구 삼청로 30",
                geo_lat=37.5786,
                geo_lon=126.9811,
            ),
            Venue(
                name="서울시립미술관",
                address="서울특별시 중구 덕수궁길 61",
                geo_lat=37.5658,
                geo_lon=126.9751,
            ),
            Venue(
                name="예술의전당 한가람미술관",
                address="서울특별시 서초구 남부순환로 2406",
                geo_lat=37.4782,
                geo_lon=127.0122,
            ),
        ]
        db.add_all(venues)
        db.commit()
        logger.info(f"{len(venues)}개 장소 생성 완료")

        # 4. Artist 생성
        logger.info("작가 생성 중...")
        artists = [
            Artist(
                name="클로드 모네",
                bio="프랑스 인상주의의 창시자. 빛과 색채의 순간적 변화를 포착하여 자연의 인상을 캔버스에 담았다.",
                email="monet@impressionism.art",
            ),
            Artist(
                name="피에르 오귀스트 르누아르",
                bio="프랑스 인상주의 화가. 햇빛 아래 사람들의 행복한 순간과 부드러운 색채를 표현했다.",
                email="renoir@impressionism.art",
            ),
            Artist(
                name="에드가 드가",
                bio="프랑스 인상주의 화가. 발레리나와 경마장 등 움직임의 순간을 포착하는 데 탁월했다.",
                email="degas@impressionism.art",
            ),
            Artist(
                name="카미유 피사로",
                bio="프랑스 인상주의 화가. 농촌 풍경과 도시의 일상을 따뜻한 시선으로 그렸다.",
                email="pissarro@impressionism.art",
            ),
            Artist(
                name="알프레드 시슬리",
                bio="영국 출신 프랑스 인상주의 화가. 하늘과 물의 반영을 섬세하게 표현했다.",
                email="sisley@impressionism.art",
            ),
        ]
        db.add_all(artists)
        db.commit()
        logger.info(f"{len(artists)}명 작가 생성 완료")

        # 5. Exhibition 생성
        logger.info("전시 생성 중...")
        exhibitions = [
            Exhibition(
                title="인상주의 걸작전: 빛의 순간",
                description_text="19세기 프랑스 인상주의 화가들의 대표작을 한자리에. 빛과 색채로 포착한 찰나의 아름다움을 만나보세요.",
                start_date=date(2025, 1, 15),
                end_date=date(2025, 4, 30),
                venue_id=venues[0].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/exhibitions/test_poster1.jpg",  # 교체 필요
            ),
            Exhibition(
                title="모네와 친구들: 지베르니의 정원",
                description_text="클로드 모네와 동료 인상주의 화가들이 그린 자연의 색채. 정원, 강, 들판의 빛나는 순간들.",
                start_date=date(2025, 2, 1),
                end_date=date(2025, 5, 31),
                venue_id=venues[1].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/exhibitions/test_poster2.jpg",  # 교체 필요
            ),
            Exhibition(
                title="인상주의의 일상: 파리의 하루",
                description_text="19세기 파리의 일상을 담은 인상주의 작품들. 카페, 극장, 거리의 생생한 순간들.",
                start_date=date(2025, 3, 1),
                end_date=date(2025, 6, 30),
                venue_id=venues[2].id,
                cover_image_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/exhibitions/test_poster3.jpg",  # 교체 필요
            ),
        ]
        db.add_all(exhibitions)
        db.commit()
        logger.info(f"{len(exhibitions)}개 전시 생성 완료")

        # 6. Artwork 생성
        logger.info("작품 생성 중...")
        artworks = [
            # 전시1: 인상주의 걸작전
            Artwork(
                title="Water Lilies",
                artist_id=artists[0].id,  # 모네
                description="모네가 말년에 지베르니 정원의 수련 연못을 그린 연작 중 하나. 물 위에 떠 있는 수련과 그 반영을 부드러운 붓터치로 표현했다.",
                year=1916,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/monet-water-lilies.webp",
            ),
            Artwork(
                title="Impression Sunrise",
                artist_id=artists[0].id,  # 모네
                description="1872년 르아브르 항구의 일출을 그린 작품. '인상주의'라는 명칭의 기원이 된 역사적인 그림이다.",
                year=1872,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/monet-impression-sunrise.jpg",
            ),
            Artwork(
                title="Bal Du Moulin De La Galette",
                artist_id=artists[1].id,  # 르누아르
                description="파리 몽마르트르 언덕의 야외 무도회장을 그린 작품. 나무 사이로 쏟아지는 햇빛과 춤추는 사람들의 즐거운 모습을 담았다.",
                year=1876,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/renoir-bal-du-moulin-de-la-galette.jpg",
            ),
            Artwork(
                title="Ballet Dancers",
                artist_id=artists[2].id,  # 드가
                description="드가가 평생 천착했던 발레 주제의 대표작. 무대 위 무희의 우아한 동작과 긴장감을 포착했다.",
                year=1878,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/degas-ballet-dancers-on-stage.jpg",
            ),
            Artwork(
                title="Absinthe",
                artist_id=artists[2].id,  # 드가
                description="파리의 카페에서 압생트를 마시는 남녀를 그린 작품. 도시 생활의 고독과 소외를 담담하게 표현했다.",
                year=1876,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/degas-absinthe.jpg",
            ),
            # 전시2: 모네와 친구들
            Artwork(
                title="Woman With Parasol",
                artist_id=artists[0].id,  # 모네
                description="모네의 첫 번째 부인 카미유와 아들 장을 그린 작품. 언덕 위에서 바람에 흔들리는 드레스와 구름이 생동감 있게 표현되었다.",
                year=1875,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/monet-woman-with-parasol.jpg",
            ),
            Artwork(
                title="Boulevard Montmartre",
                artist_id=artists[3].id,  # 피사로
                description="파리 몽마르트르 대로의 활기찬 도시 풍경. 높은 곳에서 내려다본 시점으로 거리의 움직임을 포착했다.",
                year=1897,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/pissarro-boulevard-montmartre.jpg",
            ),
            Artwork(
                title="Flood At Port Marly",
                artist_id=artists[4].id,  # 시슬리
                description="센 강이 범람한 마를리 항구의 풍경. 물에 잠긴 거리와 하늘의 반영을 서정적으로 그렸다.",
                year=1876,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/sisley-flood-at-port-marly.jpeg",
            ),
            Artwork(
                title="Rouen Cathedral",
                artist_id=artists[0].id,  # 모네
                description="모네가 루앙 대성당을 서로 다른 시간대에 그린 연작 중 하나. 빛의 변화에 따른 건물의 다양한 모습을 탐구했다.",
                year=1894,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/monet-rouen-cathedral.jpg",
            ),
            # 전시3: 인상주의의 일상
            Artwork(
                title="Girls At Piano",
                artist_id=artists[1].id,  # 르누아르
                description="피아노를 함께 연주하는 두 소녀의 평화로운 순간. 르누아르 특유의 부드러운 색채와 따뜻한 분위기가 돋보인다.",
                year=1892,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/renoir-girls-at-piano.jpg",
            ),
            Artwork(
                title="Madame Charpentier And Children",
                artist_id=artists[1].id,  # 르누아르
                description="파리 사교계의 유명 인사였던 샤르팡티에 부인과 그녀의 자녀들. 화려한 실내와 인물들의 우아함이 조화를 이룬다.",
                year=1878,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/renoir-madame-charpentier-and-children.jpg",
            ),
            Artwork(
                title="Racehorses",
                artist_id=artists[2].id,  # 드가
                description="경마장의 긴장감 넘치는 순간을 포착한 작품. 말과 기수들의 역동적인 움직임을 독특한 구도로 표현했다.",
                year=1877,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/degas-racehorses.jpg",
            ),
            Artwork(
                title="Red Roofs",
                artist_id=artists[3].id,  # 피사로
                description="프랑스 시골 마을 퐁투아즈의 전원 풍경. 붉은 지붕들과 푸른 하늘의 대비가 인상적이다.",
                year=1877,
                thumbnail_url="https://ada-lastdance-bucket.s3.ap-southeast-2.amazonaws.com/test/test-server-impressionism/artworks/pissarro-red-roofs.jpg",
            ),
        ]

        db.add_all(artworks)
        db.commit()
        logger.info(f"{len(artworks)}개 작품 생성 완료")

        # 7. Exhibition-Artwork M:N 관계 설정
        logger.info("전시-작품 연결 중...")

        # 전시1: 인상주의 걸작전 (작품 0-4)
        db.execute(
            exhibition_artworks.insert().values(
                [
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[0].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[1].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[2].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[3].id},
                    {"exhibition_id": exhibitions[0].id, "artwork_id": artworks[4].id},
                ]
            )
        )

        # 전시2: 모네와 친구들 (작품 5-8)
        db.execute(
            exhibition_artworks.insert().values(
                [
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[5].id},
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[6].id},
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[7].id},
                    {"exhibition_id": exhibitions[1].id, "artwork_id": artworks[8].id},
                ]
            )
        )

        # 전시3: 인상주의의 일상 (작품 9-12)
        db.execute(
            exhibition_artworks.insert().values(
                [
                    {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[9].id},
                    {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[10].id},
                    {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[11].id},
                    {"exhibition_id": exhibitions[2].id, "artwork_id": artworks[12].id},
                ]
            )
        )

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
            artwork_id=artworks[0].id,
            visitor_id=visitors[0].id,
            visit_id=visit.id,
            comment="빛과 색채의 조화가 아름다운 작품이네요. 인상주의의 진수를 느낄 수 있었습니다.",
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
