from rest_framework.permissions import BasePermission


class ReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"]
