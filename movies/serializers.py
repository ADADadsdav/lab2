from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Универсальный сериализатор для всех операций"""

    class Meta:
        model = Movie
        fields = ['id', 'title', 'director', 'year', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_year(self, value):
        """Валидация года выпуска"""
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1888:  # первый фильм в истории
            raise serializers.ValidationError("Год не может быть меньше 1888")
        if value > current_year + 5:  # небольшая погрешность в будущее
            raise serializers.ValidationError(f"Год не может быть больше {current_year + 5}")
        return value