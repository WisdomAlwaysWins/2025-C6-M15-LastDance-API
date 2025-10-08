"""S3 연결 테스트 스크립트"""
from app.utils.s3_client import s3_client
from PIL import Image
import io

def test_s3_connection():
    """S3 연결 및 업로드 테스트"""
    
    print("🧪 S3 연결 테스트 시작...\n")
    
    # 1. 간단한 테스트 이미지 생성
    print("1️⃣ 테스트 이미지 생성 중...")
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    print("✅ 테스트 이미지 생성 완료\n")
    
    # 2. S3에 업로드
    print("2️⃣ S3 업로드 테스트 중...")
    file_url = s3_client.upload_file(
        file_content=img_byte_arr,
        file_extension="png",
        folder="test"
    )
    
    if file_url:
        print(f"✅ 업로드 성공!")
        print(f"📎 URL: {file_url}\n")
        
        # 3. 삭제 테스트
        print("3️⃣ S3 삭제 테스트 중...")
        success = s3_client.delete_file(file_url)
        if success:
            print("✅ 삭제 성공!\n")
        else:
            print("❌ 삭제 실패\n")
        
        print("🎉 모든 테스트 통과!")
    else:
        print("❌ 업로드 실패!")
        print("\n⚠️ 확인사항:")
        print("1. .env 파일의 AWS 키가 올바른가요?")
        print("2. S3 버킷이 생성되었나요?")
        print("3. IAM 사용자에게 S3 권한이 있나요?")

if __name__ == "__main__":
    test_s3_connection()