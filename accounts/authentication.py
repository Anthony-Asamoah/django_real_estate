from django.contrib import auth, messages
from django.shortcuts import redirect


def authenticate(request):
	username = request.POST['username']
	password = request.POST['password']

	user = auth.authenticate(username=username, password=password)

	if user is not None:
		auth.login(request, user)
		messages.success(request, 'You are now logged in')
		return redirect('accounts:dashboard')
	else:
		messages.error(request, 'Invalid Credentials')
		return redirect('accounts:login')
