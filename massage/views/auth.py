from django.shortcuts import render, redirect
from django.contrib.auth import login
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
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})
