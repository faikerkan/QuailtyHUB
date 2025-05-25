from rest_framework import permissions


class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Sadece admin veya superuser erişebilir
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (
            hasattr(request.user, "is_admin") and request.user.is_admin()
        )


class IsExpertOrAdmin(permissions.BasePermission):
    """
    Sadece kalite uzmanı veya admin erişebilir
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser
            or (hasattr(request.user, "is_admin") and request.user.is_admin())
            or (hasattr(request.user, "is_expert") and request.user.is_expert())
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Sadece nesnenin sahibi veya yöneticinin erişebileceği izin sınıfı
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Süper kullanıcılar ve yöneticiler her şeyi yapabilir
        if request.user.is_superuser or (
            hasattr(request.user, "is_admin") and request.user.is_admin()
        ):
            return True

        # Kullanıcı nesneleri için
        if hasattr(obj, "username"):
            return obj == request.user

        # Değerlendirme ve çağrı nesneleri için (ileride kullanılacak)
        if hasattr(obj, "evaluator"):
            return obj.evaluator == request.user

        return False
