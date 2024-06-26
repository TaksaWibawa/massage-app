from django.shortcuts import redirect
from django.contrib import messages
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

def role_required(allowed_roles=[]):
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

def fetch_required(allowed_methods=['GET', 'POST']):
    def decorator(f):
        def wrap(request, *args, **kwargs):
            if not (request.method in allowed_methods and request.headers.get('Content-Type') == 'application/json'):
                messages.error(request, 'Invalid request.')
                return redirect('/')
            return f(request, *args, **kwargs)
        wrap.__doc__ = f.__doc__
        wrap.__name__ = f.__name__
        return wrap
    return decorator