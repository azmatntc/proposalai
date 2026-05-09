from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsProTier(permissions.BasePermission):
    """
    Restrict to Pro/Enterprise subscribers.
    """
    def has_permission(self, request, view):
        return request.user.subscription_tier in ['pro', 'enterprise']


class HasQuotaRemaining(permissions.BasePermission):
    """
    Check if user has remaining AI quota.
    """
    def has_permission(self, request, view):
        return not request.user.has_reached_quota()
