"""
AWS Lambda 클라이언트
"""

import json
from typing import List

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

    def generate_embedding(self, image_base64: str) -> List[float]:
        """
        Lambda 함수 호출하여 단일 이미지 임베딩 생성

        Args:
            image_base64 (str): Base64 인코딩된 이미지

        Returns:
            List[float]: 384차원 임베딩 벡터

        Raises:
            Exception: Lambda 실행 실패 시
        """

        payload = {
            "body": json.dumps({"image_base64": image_base64}),
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
            embedding = body.get("embedding")
            dimension = body.get("dimension")

            if not embedding:
                raise Exception("Lambda가 임베딩을 반환하지 않았습니다")

            if dimension != 384:
                raise Exception(f"잘못된 임베딩 차원: {dimension} (예상: 384)")

            return embedding
        else:
            error_body = result.get("body", "{}")
            if isinstance(error_body, str):
                error_body = json.loads(error_body)
            raise Exception(f"Lambda 오류: {error_body.get('error', result)}")


lambda_client = LambdaClient()
