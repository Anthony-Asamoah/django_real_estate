from django.contrib import auth, messages
from django.shortcuts import redirect, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme


def post_login_url(request, user):
    """Where to send a user after signing in: an explicit safe ``next``, else by role."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    if user.is_staff or user.is_superuser:
        return '/cms/'
    return resolve_url('accounts:dashboard')


def authenticate(request):
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        messages.success(request, 'You are now logged in')
        return redirect(post_login_url(request, user))

    messages.error(request, 'Invalid Credentials')
    login_url = resolve_url('accounts:login')
    next_url = request.POST.get('next')
    if next_url:
        login_url += f'?next={next_url}'
    return redirect(login_url)
