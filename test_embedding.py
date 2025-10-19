# test_embedding.py
"""HuggingFace API 임베딩 서비스 테스트 (EC2 프리티어용)"""
import os
from PIL import Image
import numpy as np

def test_embedding_service():
    """임베딩 서비스 테스트"""
    
    print("🧪 임베딩 서비스 테스트 시작...")
    
    # 1. 서비스 초기화
    print("\n1️⃣ HuggingFace API 서비스 초기화")
    try:
        from app.utils.embedding import HuggingFaceEmbeddingService
        service = HuggingFaceEmbeddingService()
        print("✅ 초기화 완료")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        return False
    
    # 2. 테스트 이미지 생성
    print("\n2️⃣ 테스트 이미지 생성")
    test_image = Image.new('RGB', (224, 224), color='red')
    print("✅ 테스트 이미지 생성 완료")
    
    # 3. 임베딩 생성
    print("\n3️⃣ 임베딩 생성 중... (HuggingFace API 호출, 10-30초 소요)")
    try:
        embedding = service.get_embedding(test_image)
        print(f"✅ 임베딩 생성 완료!")
        print(f"   - Shape: {embedding.shape}")
        print(f"   - Type: {type(embedding)}")
        print(f"   - 첫 5개 값: {embedding[:5]}")
        
    except Exception as e:
        print(f"❌ 임베딩 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 유사도 계산 테스트
    print("\n4️⃣ 유사도 계산 테스트")
    test_image2 = Image.new('RGB', (224, 224), color='blue')
    
    print("   두 번째 이미지 임베딩 생성 중...")
    try:
        embedding2 = service.get_embedding(test_image2)
        similarity = service.compute_similarity(embedding, embedding2)
        
        print(f"✅ 유사도 계산 완료!")
        print(f"   - 유사도: {similarity:.4f}")
        
    except Exception as e:
        print(f"❌ 유사도 계산 실패: {e}")
        return False
    
    # 5. 같은 이미지 유사도 (1에 가까워야 함)
    print("\n5️⃣ 동일 이미지 유사도 테스트")
    same_similarity = service.compute_similarity(embedding, embedding)
    print(f"   - 동일 이미지 유사도: {same_similarity:.4f}")
    
    if same_similarity > 0.99:
        print("✅ 정상 (0.99 이상)")
    else:
        print("⚠️  비정상 (0.99 미만)")
    
    print("\n🎉 모든 테스트 완료!")
    return True


def test_real_image():
    """실제 이미지로 테스트 (선택)"""
    
    image_path = input("\n이미지 파일 경로 입력 (Enter로 스킵): ").strip()
    
    if not image_path:
        print("⏭️  실제 이미지 테스트 스킵")
        return
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없음: {image_path}")
        return
    
    print(f"\n📸 실제 이미지 테스트: {image_path}")
    
    try:
        # 이미지 로드
        image = Image.open(image_path).convert('RGB')
        print(f"✅ 이미지 로드 완료: {image.size}")
        
        # 임베딩 생성
        from app.utils.embedding import HuggingFaceEmbeddingService
        service = HuggingFaceEmbeddingService()
        print("⏳ 임베딩 생성 중...")
        embedding = service.get_embedding(image)
        
        print(f"✅ 임베딩 생성 완료!")
        print(f"   - Shape: {embedding.shape}")
        print(f"   - 평균: {embedding.mean():.4f}")
        print(f"   - 표준편차: {embedding.std():.4f}")
        
    except Exception as e:
        print(f"❌ 실제 이미지 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 환경 변수 확인
    from app.config import settings
    
    print("=" * 60)
    print("🤗 HuggingFace API 임베딩 서비스 테스트 (EC2 프리티어용)")
    print("=" * 60)
    
    # 토큰 확인
    try:
        token = settings.HUGGINGFACE_TOKEN
        if not token or token == "hf_...":
            print("❌ HUGGINGFACE_TOKEN이 설정되지 않았습니다!")
            print("   .env 파일에 토큰을 추가해주세요.")
            exit(1)
        
        print(f"✅ HuggingFace Token: {token[:10]}...")
        print()
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        exit(1)
    
    # 기본 테스트
    success = test_embedding_service()
    
    # 실제 이미지 테스트
    if success:
        test_real_image()