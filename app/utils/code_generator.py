"""
로그인 코드 생성 유틸
"""

import random
import string


def generate_login_code(length: int = 6) -> str:
    """
    6자리 로그인 코드 생성
    - 숫자, 영어 대소문자, 특수문자 포함

    Args:
        length: 코드 길이 (기본 6)

    Returns:
        생성된 코드 (예: "aB3!x9")
    """
    # 문자 풀
    digits = string.digits  # 0-9
    lowercase = string.ascii_lowercase  # a-z
    uppercase = string.ascii_uppercase  # A-Z
    special = "!@#$%^&*"  # 특수문자

    all_chars = digits + lowercase + uppercase + special

    # 각 타입에서 최소 1개씩 보장
    code = [
        random.choice(digits),
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(special),
    ]

    # 나머지 자리 랜덤 채우기
    for _ in range(length - 4):
        code.append(random.choice(all_chars))

    # 섞기
    random.shuffle(code)

    return "".join(code)


def is_valid_login_code(code: str) -> bool:
    """
    로그인 코드 형식 검증

    Args:
        code: 검증할 코드

    Returns:
        유효 여부
    """
    if len(code) != 6:
        return False

    has_digit = any(c.isdigit() for c in code)
    has_lower = any(c.islower() for c in code)
    has_upper = any(c.isupper() for c in code)
    has_special = any(c in "!@#$%^&*" for c in code)

    return has_digit and has_lower and has_upper and has_special
