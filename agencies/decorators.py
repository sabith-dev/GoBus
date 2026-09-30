from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def agency_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to your agency account.")
            return redirect("agency:login")
        if request.user.role != "agency":
            messages.error(request, "You do not have permission to access this page.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return _wrapped
