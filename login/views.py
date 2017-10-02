from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from django.conf import settings


def auth_login(request):
    next_page = request.GET.get('next', '/annotation/')
    if request.user.is_authenticated():
        return redirect(next_page)

    if request.method == 'POST':
        user_form = AuthenticationForm(data=request.POST)
        if user_form.is_valid():
            user = authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password'])
            # user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect(next_page)
        else:
            return render(request, 'login.html', {'form': user_form})
    return render(request, 'login.html', {'form': AuthenticationForm()})


def auth_logout(request):
    logout(request)
    return redirect('/annotation/')
