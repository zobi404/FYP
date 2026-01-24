from rest_framework import permissions

class IsTester(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tester'

class IsMaintainer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'maintainer'

class IsReportOwnerOrMaintainer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'maintainer':
            # Check if user is maintainer of the project
            return obj.project.maintainer == request.user
        if request.user.role == 'tester':
            # Check if user is the one who reported it
            return obj.tester == request.user
        return False

class IsMaintainerOfProject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.project.maintainer == request.user
