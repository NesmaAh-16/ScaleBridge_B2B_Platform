from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            if not (request.user.is_superuser or request.user.role in roles):
                return HttpResponseForbidden(
                    '403 Forbidden: You do not have permission to access this page.'
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator