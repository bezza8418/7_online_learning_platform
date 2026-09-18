from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerProfile(permissions.BasePermission):
    """Проверяет, что пользователь редактирует свой профиль"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
