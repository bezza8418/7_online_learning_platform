from urllib.parse import urlparse
from rest_framework import serializers


class YouTubeValidator:
    """Валидатор, проверяющий, что ссылка ведёт только на youtube.com"""

    ALLOWED_DOMAINS = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be', 'm.youtube.com']

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        tmp_val = value.get(self.field) if isinstance(value, dict) else value

        if tmp_val:
            parsed = urlparse(tmp_val)
            domain = parsed.netloc.lower()

            if domain not in self.ALLOWED_DOMAINS:
                raise serializers.ValidationError(
                    'Ссылка должна вести только на youtube.com. '
                    'Ссылки на сторонние ресурсы запрещены.'
                )
        return tmp_val
