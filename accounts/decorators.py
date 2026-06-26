from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if not (request.user.is_superuser or request.user.role in roles):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:profile')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
