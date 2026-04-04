from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from users.models import User, UserToken
from .jwt_service import JWTService
from django.db import models


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    def generate_tokens_for_user(user: User) -> dict:
        """Генерация токенов для пользователя (используется при OAuth)"""
        # Генерируем токены
        access_token = JWTService.generate_access_token(user.id)
        refresh_token = JWTService.generate_refresh_token(user.id)

        # Получаем время истечения
        access_exp = datetime.utcnow() + timedelta(seconds=int(settings.JWT_ACCESS_EXPIRATION))
        refresh_exp = datetime.utcnow() + timedelta(seconds=int(settings.JWT_REFRESH_EXPIRATION))

        # Сохраняем токены в БД
        JWTService.save_token(user, access_token, 'access', access_exp)
        JWTService.save_token(user, refresh_token, 'refresh', refresh_exp)

        return {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @staticmethod
    def register_user(email: str, username: str, password: str) -> User:
        """Регистрация нового пользователя"""
        # Проверяем уникальность
        if User.objects.filter(email=email).exists():
            raise ValueError('Email уже зарегистрирован')

        if User.objects.filter(username=username).exists():
            raise ValueError('Username уже занят')

        # Создаем пользователя
        user = User.objects.create(
            email=email,
            username=username
        )
        user.set_password(password)
        user.save()

        return user

    @staticmethod
    def login_user(identifier: str, password: str) -> dict:
        """Вход пользователя по email или username"""
        # Ищем пользователя по email или username
        user = User.objects.filter(
            models.Q(email=identifier) | models.Q(username=identifier),
            deleted_at__isnull=True
        ).first()

        if not user:
            raise ValueError('Неверные учетные данные')

        if not user.check_password(password):
            raise ValueError('Неверные учетные данные')

        return AuthService.generate_tokens_for_user(user)

    @staticmethod
    def refresh_tokens(refresh_token: str) -> dict:
        """Обновление пары токенов"""
        # Проверяем refresh token
        payload = JWTService.verify_refresh_token(refresh_token)
        if not payload:
            raise ValueError('Невалидный refresh токен')

        user_id = payload.get('user_id')

        # Проверяем, не отозван ли токен
        token_hash = UserToken.hash_token(refresh_token)
        stored_token = UserToken.objects.filter(
            token_hash=token_hash,
            token_type='refresh',
            is_revoked=False
        ).first()

        if not stored_token or not stored_token.is_valid():
            raise ValueError('Refresh токен отозван или истек')

        # Отзываем старый refresh token
        stored_token.is_revoked = True
        stored_token.save()

        # Получаем пользователя
        user = User.active_objects.get(id=user_id)

        return AuthService.generate_tokens_for_user(user)

    @staticmethod
    def logout_user(access_token: str, refresh_token: str = None):
        """Выход пользователя (отзыв текущих токенов)"""
        # Отзываем access token
        JWTService.revoke_token(access_token)

        # Отзываем refresh token если есть
        if refresh_token:
            JWTService.revoke_token(refresh_token)

    @staticmethod
    def logout_all_sessions(user: User):
        """Завершение всех сессий пользователя"""
        JWTService.revoke_all_user_tokens(user)