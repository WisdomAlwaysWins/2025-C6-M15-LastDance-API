# app/db/seed.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import (
    TagCategory, Tag, Venue, Artist, 
    Exhibition, Artwork, Visitor
)
from datetime import date

def seed_database():
    """가상의 전시 데이터로 데이터베이스 시딩"""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # 1. TagCategory 생성
        print("🏷️  Creating TagCategories...")
        categories = [
            TagCategory(name="감각", color_hex="#FF6B9D", display_order=1),
            TagCategory(name="시간", color_hex="#4ECDC4", display_order=2),
            TagCategory(name="공간", color_hex="#FFE66D", display_order=3),
            TagCategory(name="질감", color_hex="#95E1D3", display_order=4)
        ]
        db.add_all(categories)
        db.commit()
        print(f"   ✓ Created {len(categories)} categories")
        
        # 2. Tag 생성
        print("🎨 Creating Tags...")
        tags = [
            # 감각 (category_id=1)
            Tag(name="몽환적인", category_id=1, display_order=1),
            Tag(name="날카로운", category_id=1, display_order=2),
            Tag(name="부드러운", category_id=1, display_order=3),
            Tag(name="강렬한", category_id=1, display_order=4),
            Tag(name="고요한", category_id=1, display_order=5),
            
            # 시간 (category_id=2)
            Tag(name="영원한", category_id=2, display_order=1),
            Tag(name="순간적인", category_id=2, display_order=2),
            Tag(name="느린", category_id=2, display_order=3),
            Tag(name="빠른", category_id=2, display_order=4),
            Tag(name="정지된", category_id=2, display_order=5),
            
            # 공간 (category_id=3)
            Tag(name="넓은", category_id=3, display_order=1),
            Tag(name="좁은", category_id=3, display_order=2),
            Tag(name="깊은", category_id=3, display_order=3),
            Tag(name="얕은", category_id=3, display_order=4),
            Tag(name="무한한", category_id=3, display_order=5),
            
            # 질감 (category_id=4)
            Tag(name="매끄러운", category_id=4, display_order=1),
            Tag(name="거친", category_id=4, display_order=2),
            Tag(name="투명한", category_id=4, display_order=3),
            Tag(name="불투명한", category_id=4, display_order=4),
            Tag(name="흐릿한", category_id=4, display_order=5)
        ]
        db.add_all(tags)
        db.commit()
        print(f"   ✓ Created {len(tags)} tags")
        
        # 3. Venue 생성
        print("🏛️  Creating Venues...")
        venues = [
            Venue(
                name="루미나 갤러리",
                address="서울특별시 종로구 빛의거리 42",
                geo_lat=37.5799,
                geo_lon=126.9770
            ),
            Venue(
                name="에테르 아트홀",
                address="서울특별시 강남구 공간로 128",
                geo_lat=37.5172,
                geo_lon=127.0473
            ),
            Venue(
                name="크로노스 미술관",
                address="서울특별시 용산구 시간의길 7",
                geo_lat=37.5326,
                geo_lon=126.9900
            )
        ]
        db.add_all(venues)
        db.commit()
        print(f"   ✓ Created {len(venues)} venues")
        
        # 4. Artist 생성
        print("🎭 Creating Artists...")
        artists = [
            Artist(
                name="나비야",
                bio="빛과 그림자를 탐구하는 설치 작가. 공간의 본질을 재해석한다.",
                email="naviya@artmail.com"
            ),
            Artist(
                name="린 카이",
                bio="시간의 흐름을 시각화하는 영상 작가. 순간과 영원 사이를 넘나든다.",
                email="lin.kai@artmail.com"
            ),
            Artist(
                name="제로 문",
                bio="무의식의 풍경을 그리는 화가. 꿈과 현실의 경계를 허문다.",
                email="zero.moon@artmail.com"
            ),
            Artist(
                name="소라 진",
                bio="소리를 조각하는 사운드 아티스트. 침묵 속에서 울림을 찾는다.",
                email="sora.jin@artmail.com"
            ),
            Artist(
                name="아리스",
                bio="감정의 색채를 담는 미디어 아티스트. 마음의 스펙트럼을 표현한다.",
                email="aris@artmail.com"
            )
        ]
        db.add_all(artists)
        db.commit()
        print(f"   ✓ Created {len(artists)} artists")
        
        # 5. Exhibition 생성
        print("🖼️  Creating Exhibitions...")
        exhibitions = [
            Exhibition(
                title="빛의 기억",
                description="빛과 어둠이 만나는 지점에서 기억을 소환하다. 잊혀진 순간들이 빛을 통해 되살아나는 감각적 여정.",
                start_date=date(2025, 1, 15),
                end_date=date(2025, 4, 15),
                venue_id=venues[0].id,
                poster_image_url="https://picsum.photos/seed/light-memory/800/1200"
            ),
            Exhibition(
                title="시간의 파편",
                description="흩어진 시간의 조각들을 모아 새로운 우주를 구축하다. 과거와 미래가 현재에서 만나는 시공간적 실험.",
                start_date=date(2025, 2, 1),
                end_date=date(2025, 5, 31),
                venue_id=venues[1].id,
                poster_image_url="https://picsum.photos/seed/time-fragments/800/1200"
            ),
            Exhibition(
                title="무의식의 정원",
                description="잠든 마음 속 정원을 거닐다. 의식 너머 펼쳐진 내면의 풍경을 시각적으로 탐험하는 초현실적 전시.",
                start_date=date(2025, 3, 10),
                end_date=date(2025, 6, 30),
                venue_id=venues[2].id,
                poster_image_url="https://picsum.photos/seed/unconscious-garden/800/1200"
            )
        ]
        db.add_all(exhibitions)
        db.commit()
        
        # Exhibition-Artist 관계 설정
        exhibitions[0].artists.extend([artists[0], artists[1]])  # 나비야, 린 카이
        exhibitions[1].artists.extend([artists[1], artists[2]])  # 린 카이, 제로 문
        exhibitions[2].artists.extend([artists[2], artists[3], artists[4]])  # 제로 문, 소라 진, 아리스
        db.commit()
        print(f"   ✓ Created {len(exhibitions)} exhibitions")
        
        # 6. Artwork 생성
        print("🎨 Creating Artworks...")
        artworks = [
            # 빛의 기억 전시 작품들
            Artwork(
                title="새벽의 속삭임",
                exhibition_id=exhibitions[0].id,
                artist_id=artists[0].id,
                description="빛이 어둠을 깨우는 순간, 하루가 시작되기 전 고요한 대화",
                year=2024,
                image_url="https://picsum.photos/seed/dawn-whisper/1000/800"
            ),
            Artwork(
                title="잊혀진 파장",
                exhibition_id=exhibitions[0].id,
                artist_id=artists[0].id,
                description="기억 속에 남은 빛의 떨림, 시간이 남긴 흔적",
                year=2024,
                image_url="https://picsum.photos/seed/forgotten-wave/1000/800"
            ),
            Artwork(
                title="투명한 메아리",
                exhibition_id=exhibitions[0].id,
                artist_id=artists[1].id,
                description="빛이 공간을 통과하며 남긴 소리 없는 울림",
                year=2023,
                image_url="https://picsum.photos/seed/transparent-echo/1000/800"
            ),
            
            # 시간의 파편 전시 작품들
            Artwork(
                title="정지된 흐름",
                exhibition_id=exhibitions[1].id,
                artist_id=artists[1].id,
                description="멈춘 듯 흐르는 시간, 역설의 시각화",
                year=2024,
                image_url="https://picsum.photos/seed/frozen-flow/1000/800"
            ),
            Artwork(
                title="순간의 무게",
                exhibition_id=exhibitions[1].id,
                artist_id=artists[2].id,
                description="찰나가 품은 영원함, 시간의 밀도를 느끼다",
                year=2024,
                image_url="https://picsum.photos/seed/moment-weight/1000/800"
            ),
            Artwork(
                title="과거의 미래",
                exhibition_id=exhibitions[1].id,
                artist_id=artists[2].id,
                description="지나간 시간이 예견한 다가올 세계",
                year=2023,
                image_url="https://picsum.photos/seed/past-future/1000/800"
            ),
            
            # 무의식의 정원 전시 작품들
            Artwork(
                title="꿈의 나무",
                exhibition_id=exhibitions[2].id,
                artist_id=artists[2].id,
                description="잠든 마음에서 자라는 환상의 숲",
                year=2024,
                image_url="https://picsum.photos/seed/dream-tree/1000/800"
            ),
            Artwork(
                title="침묵의 꽃",
                exhibition_id=exhibitions[2].id,
                artist_id=artists[3].id,
                description="소리 없이 피어나는 내면의 아름다움",
                year=2024,
                image_url="https://picsum.photos/seed/silent-flower/1000/800"
            ),
            Artwork(
                title="감정의 스펙트럼",
                exhibition_id=exhibitions[2].id,
                artist_id=artists[4].id,
                description="보이지 않는 감정을 가시화한 색의 향연",
                year=2024,
                image_url="https://picsum.photos/seed/emotion-spectrum/1000/800"
            ),
            Artwork(
                title="내면의 거울",
                exhibition_id=exhibitions[2].id,
                artist_id=artists[4].id,
                description="마주하기 두려운 자신을 비추는 투명한 성찰",
                year=2023,
                image_url="https://picsum.photos/seed/inner-mirror/1000/800"
            )
        ]
        db.add_all(artworks)
        db.commit()
        print(f"   ✓ Created {len(artworks)} artworks")
        
        # 7. Visitor 생성
        print("👥 Creating Visitors...")
        visitors = [
            Visitor(uuid="visitor-alpha-001", name="알파"),
            Visitor(uuid="visitor-beta-002", name="베타"),
            Visitor(uuid="visitor-gamma-003", name="감마"),
            Visitor(uuid="visitor-delta-004", name="델타"),
            Visitor(uuid="visitor-epsilon-005", name="엡실론")
        ]
        db.add_all(visitors)
        db.commit()
        print(f"   ✓ Created {len(visitors)} visitors")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"""
📊 Summary:
   - {len(categories)} Tag Categories
   - {len(tags)} Tags
   - {len(venues)} Venues
   - {len(artists)} Artists
   - {len(exhibitions)} Exhibitions
   - {len(artworks)} Artworks
   - {len(visitors)} Visitors
        """)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()