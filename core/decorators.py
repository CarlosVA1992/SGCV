from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Permite el acceso solo a usuarios autenticados que pertenezcan
    a alguno de los grupos indicados. Superusuarios siempre pasan.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not request.user.groups.filter(name__in=roles).exists():
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator