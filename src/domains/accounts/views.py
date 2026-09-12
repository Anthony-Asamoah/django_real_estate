from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from wagtail.admin.views.account import LoginView as WagtailLoginView

from domains.inquiries.models import ProjectInquiry
from infrastructure import recaptcha
from .authentication import authenticate, post_login_url
from .validation import validator


class CMSLoginView(WagtailLoginView):
    def post(self, request, *args, **kwargs):
        if not recaptcha.verify(request.POST.get('g-recaptcha-response', ''), 'cms_login'):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)


def login(request):
    if request.user.is_authenticated:
        return redirect(post_login_url(request, request.user))
    if request.method == 'POST':
        return authenticate(request)
    return render(request, 'accounts/login.html', {'next': request.GET.get('next', '')})


def register(request):
    if request.method == 'POST':
        return validator(request)
    else:
        return render(request, 'accounts/sign-up.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')

        return redirect('/')


@login_required
def dashboard(request):
    user_contacts = ProjectInquiry.objects.order_by('-timestamp').filter(user_id=request.user.id)

    return render(request, 'accounts/dashboard.html', {'contacts': user_contacts})
