"""
AWS Lambda 함수: 단일 이미지 임베딩 생성
DINOv2-small 모델 사용
"""
import json
import torch
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np
import io
import base64
import os

# Lambda /tmp 폴더 사용 (쓰기 가능)
os.environ['TRANSFORMERS_CACHE'] = '/tmp/huggingface'
os.environ['HF_HOME'] = '/tmp/huggingface'

# DINOv2 모델 (글로벌 변수 - 콜드 스타트 최적화)
MODEL = None
PROCESSOR = None
DEVICE = None


def load_model():
    """DINOv2 모델 로드 (첫 실행 시 한 번만)"""
    global MODEL, PROCESSOR, DEVICE
    
    if MODEL is None:
        print("🦖 DINOv2 모델 로딩 중...")
        
        DEVICE = torch.device("cpu")
        model_name = "facebook/dinov2-small"
        
        PROCESSOR = AutoImageProcessor.from_pretrained(model_name)
        MODEL = AutoModel.from_pretrained(model_name).to(DEVICE)
        MODEL.eval()
        
        print("✅ 모델 로딩 완료!")


def get_embedding(image: Image.Image) -> np.ndarray:
    """이미지에서 임베딩 추출 (384차원)"""
    inputs = PROCESSOR(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = MODEL(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    
    return embedding.squeeze()


def handler(event, context):
    """
    Lambda 핸들러
    
    Request:
    {
        "image_base64": "iVBORw0KGgoAAAANS..."
    }
    
    또는 Warming up:
    {
        "warmup": true
    }
    
    Response:
    {
        "embedding" : [0.123, 0.456, ...], // 384차원 벡터
        "dimension" : 384
    }
    """
    
    # CORS 헤더
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        # ✅ 워밍업 요청 체크
        if event.get('warmup'):
            print("🔥 Warming up... 모델 로드 유지")
            load_model()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'warmed up', 'status': 'ready'})
            }
        
        # OPTIONS 요청 (CORS preflight)
        if event.get('httpMethod') == 'OPTIONS' or event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        print(f"📨 Lambda 실행 시작: 임베딩 생성")
        
        # 모델 로드
        load_model()
        
        # Body 파싱
        body_str = event.get('body', '{}')
        
        # API Gateway v2는 base64 인코딩 가능
        if event.get('isBase64Encoded', False):
            body_str = base64.b64decode(body_str).decode('utf-8')
        
        body = json.loads(body_str)
        image_base64 = body.get('image_base64')
        
        # Validation
        if not image_base64:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'image_base64 필드가 필요합니다',
                    'example': {
                        'image_base64': 'base64_encoded_image_string',
                    }
                })
            }
        
        print(f"🖼️  이미지 디코딩 중...")
        
        # Base64 디코딩
        try:
            image_bytes = base64.b64decode(image_base64)
            uploaded_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            print(f"✅ 업로드 이미지 로드: {uploaded_image.size}")
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'이미지 디코딩 실패: {str(e)}'})
            }
        
        # 업로드된 이미지의 임베딩 생성
        print(f"🧠 이미지 임베딩 생성 중...")
        embedding = get_embedding(uploaded_image)
        print(f"✅ 임베딩 생성 완료: shape {embedding.shape}")

        # NumPy array → Python list 변환
        embedding_list = embedding.tolist()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'embedding': embedding_list,
                'dimension': len(embedding_list)
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }