"""
작가 이모지 상수
"""

# 허용된 이모지 타입 (5가지)
ALLOWED_EMOJI_TYPES = [
    "emoji_heart",
    "emoji_like",
    "emoji_surprise",
    "emoji_sad",
    "emoji_laugh",
]

# 이모지 설명 (문서화용)
EMOJI_DESCRIPTIONS = {
    "emoji_emoji_heart": "하트",
    "emoji_like": "좋아요",
    "emoji_surprise": "놀람",
    "emoji_sad": "슬픔",
    "emoji_laugh": "하하",
}


def is_valid_emoji_type(emoji_type: str) -> bool:
    """
    이모지 타입 유효성 검증

    Args:
        emoji_type: 검증할 이모지 타입

    Returns:
        유효 여부
    """
    return emoji_type in ALLOWED_EMOJI_TYPES
