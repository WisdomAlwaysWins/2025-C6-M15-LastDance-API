"""
AWS Lambda 클라이언트
"""

import json
from typing import Any, Dict, List

import boto3

from app.config import settings


class LambdaClient:
    def __init__(self):
        self.client = boto3.client(
            "lambda",
            region_name=settings.AWS_LAMBDA_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.function_name = "lastdance-embedding-generator"

    def invoke_image_matching(
        self, image_base64: str, artworks: List[Dict[str, Any]], threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Lambda 함수 호출하여 이미지 매칭

        Args:
            image_base64: Base64 인코딩된 이미지
            artworks: 작품 정보 리스트 [{"id": 1, "title": "...", "thumbnail_url": "..."}]
            threshold: 유사도 임계값
        """
        payload = {
            "body": json.dumps(
                {
                    "image_base64": image_base64,
                    "artworks": artworks,
                    "threshold": threshold,
                }
            ),
            "httpMethod": "POST",
        }

        response = self.client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        result = json.loads(response["Payload"].read())

        if result.get("statusCode") == 200:
            body = json.loads(result.get("body", "{}"))
            return body
        else:
            raise Exception(f"Lambda error: {result}")


lambda_client = LambdaClient()
