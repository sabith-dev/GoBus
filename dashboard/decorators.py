from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_portal:login')
        if not (request.user.is_superuser or request.user.user_type == 'admin'):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper