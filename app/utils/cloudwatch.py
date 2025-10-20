import logging
import sys

import boto3
import watchtower
from botocore.exceptions import NoCredentialsError

from app.config import settings

logger = logging.getLogger(__name__)


def setup_cloudwatch_logging():
    """
    CloudWatch Logs 설정
    
    환경별로 로그 그룹 분리:
    - /lastdance/production/api
    - /lastdance/test/api
    """
    try:
        # 환경별 로그 그룹
        log_group = f"/lastdance/{settings.ENVIRONMENT}/api"
        
        # boto3 client 생성 (region 명시)
        boto3_client = boto3.client(
            "logs",
            region_name=settings.AWS_REGION,  
        )
        
        # CloudWatch Handler 생성
        cloudwatch_handler = watchtower.CloudWatchLogHandler(
            log_group=log_group,
            stream_name="{machine_name}/{program_name}/{logger_name}",
            use_queues=True,
            create_log_group=False,
            boto3_client=boto3_client,  
        )
        
        # 포맷 설정
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        cloudwatch_handler.setFormatter(formatter)
        
        # Root Logger에 추가
        root_logger = logging.getLogger()
        root_logger.addHandler(cloudwatch_handler)
        root_logger.setLevel(logging.INFO)
        
        logger.info(f"CloudWatch Logs 설정 완료: {log_group}")
        
    except NoCredentialsError:
        logger.warning("AWS 자격 증명 없음 - CloudWatch Logs 비활성화")
        
    except Exception as e:
        logger.error(f"CloudWatch Logs 설정 실패: {e}")
        # 로컬 로깅은 계속
        pass


def setup_console_logging():
    """
    콘솔 로깅 설정 (기본)
    """
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(levelname)s:\t%(message)s"
    )
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # 로그 추가!
    logger.info("콘솔 로깅 설정 완료 (로컬 개발 모드)")