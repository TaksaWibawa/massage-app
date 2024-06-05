from django.shortcuts import redirect
from functools import wraps

def auth_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrap

def protected(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return function(request, *args, **kwargs)
    return wrap

def supervisor_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            elif request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            elif any(request.user.groups.filter(name__iexact=role).exists() for role in allowed_roles):
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/')
        return _wrapped_view
    return decorator