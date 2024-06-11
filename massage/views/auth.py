from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from massage.forms import LoginForm
from massage.decorator import protected

@protected
def LoginPage(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, 'Login successful.')
            if form.user.groups.filter(name__iexact='supervisor').exists():
                return redirect('chart')
            elif form.user.groups.filter(name__iexact='accountant').exists():
                return redirect('recap')
            elif form.user.groups.filter(name__iexact='employee').exists():
                return redirect('recap')
            else:
                return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def Logout(request):
    if request.user.is_authenticated:
        request.session.flush()
        logout(request)
        messages.success(request, 'Logout successful.')
    return redirect('login')