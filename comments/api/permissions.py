from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    check obj.user == request.user
    general class
    Permission will be exec one by one
    detail=False action, check has_permission
    detail=True action, check has_permission and has_object_permission
    if error, error message display IsObjectOwner.message content
    """
    message = "You do not have permission to access this object."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user