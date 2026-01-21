from rest_framework import permissions

class IsMaintainerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow maintainers to create projects.
    Only the project owner generally can update or delete it.
    """

    def has_permission(self, request, view):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to authenticated maintainers
        return request.user.is_authenticated and request.user.role == 'maintainer'

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (or check visibility)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the project
        return obj.maintainer == request.user
