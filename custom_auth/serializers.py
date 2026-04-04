from rest_framework import serializers
from users.models import User
import re


class RegisterSerializer(serializers.Serializer):
    """Сериализатор для регистрации"""
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        """Проверка уникальности email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email уже зарегистрирован')
        return value

    def validate_username(self, value):
        """Проверка уникальности username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username уже занят')
        if len(value) < 3:
            raise serializers.ValidationError('Username должен быть не менее 3 символов')
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError('Username может содержать только буквы, цифры и _')
        return value

    def validate_password(self, value):
        """Проверка сложности пароля"""
        if len(value) < 8:
            raise serializers.ValidationError('Пароль должен быть не менее 8 символов')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Пароль должен содержать хотя бы одну цифру')
        return value

    def validate(self, data):
        """Проверка совпадения паролей"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают'})
        return data


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа"""
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа с данными пользователя"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = fields


class ForgotPasswordSerializer(serializers.Serializer):
    """Сериализатор для запроса сброса пароля"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Сериализатор для сброса пароля"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Пароли не совпадают'})
        return data