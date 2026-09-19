from rest_framework import serializers


class YouTubeValidator:
    """Валидатор, проверяющий, что ссылка ведёт только на youtube.com"""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение поля из входных данных
        tmp_val = value.get(self.field) if isinstance(value, dict) else value

        if tmp_val:
            if 'youtube.com' not in tmp_val and 'youtu.be' not in tmp_val:
                raise serializers.ValidationError(
                    'Ссылка должна вести только на youtube.com. '
                    'Ссылки на сторонние ресурсы запрещены.'
                )
        return tmp_val
