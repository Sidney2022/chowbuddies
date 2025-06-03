from rest_framework.permissions import BasePermission, SAFE_METHODS
    

class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        # Allow authenticated users to access the endpoint
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins can access any object, regular users can only access their own
        return request.user.is_staff or obj == request.user
    
class IsAdminOrSuperuser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff 


class IsProducer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_producer
    
# class IsProducerorReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         return request.user and request.user.is_producer

class IsOwnerOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.producer.user_id == request.user or request.user.is_staff or request.user.is_superuser

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        print("request.user", request.user.id, "obj", obj, obj.id)
        return obj.id == request.user.id# or obj.id == request.user


class IsActualUser(BaseException):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return obj.producer.user_id == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit, others can only read.
    """
    def has_permission(self, request, view):
        # Read-only for non-admins
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions for admins only
        return request.user and request.user.is_staff