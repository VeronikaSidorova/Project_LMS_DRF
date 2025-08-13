import re

from rest_framework.serializers import ValidationError


def validate_video_link(value):
    """Validate that the link is a valid YouTube link."""
    youtube_regex = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")

    if not youtube_regex.match(value):
        raise ValidationError("Ссылки на видео должны быть только с youtube.com.")

    return value
