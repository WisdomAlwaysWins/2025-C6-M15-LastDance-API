FROM public.ecr.aws/lambda/python:3.11

# 작업 디렉토리
WORKDIR ${LAMBDA_TASK_ROOT}

# requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Lambda 핸들러만 복사 (app/ 폴더 제외!)
COPY lambda_handler.py .

# 핸들러 설정
CMD ["lambda_handler.handler"]