from rest_framework import permissions

class AdminPermissionOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        else:
            return request.user.is_authenticated and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True
        else:
            return request.user.is_authenticated and request.user.is_superuser
