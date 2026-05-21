from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Разрешение на уровне объекта: только владелец"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user