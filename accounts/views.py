from django.shortcuts import render, redirect
from django.contrib import auth, messages
from .validation import validator
from .authentication import authenticate

# Create your views here.


def login(request):
	if request.method == 'POST':
		return authenticate(request)
	else:
		return render(request, 'accounts/login.html')


def register(request):
	if request.method == 'POST':
		return validator(request)
	else:
		return render(request, 'accounts/sign-up.html')


def logout(request):
	if request.method == 'POST':
		auth.logout(request)
		messages.success(request, 'You are now logged out')

		return redirect('pages:index')


def dashboard(request):
	return render(request, 'accounts/dashboard.html')
