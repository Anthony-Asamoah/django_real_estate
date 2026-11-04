from django.contrib import messages
from django.contrib.auth.models import User as user
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils import timezone


def validator(request):
    # get data
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password2']
    email = request.POST['email']

    # Validate details
    if password != password2:
        messages.error(request, 'Passwords Do Not Match!')
        return redirect('accounts:register')

    if user.objects.filter(username=username).exists():
        messages.error(request, 'Username is already taken')
        return redirect('accounts:register')

    if user.objects.filter(email=email).exists():
        messages.error(request, 'email is already registered')
        return redirect('accounts:register')

    new_user = user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        date_joined=timezone.now(),
    )

    # FR-6.6: run AUTH_PASSWORD_VALIDATORS (user passed so similarity check works)
    try:
        validate_password(password, new_user)
    except ValidationError as e:
        for msg in e.messages:
            messages.error(request, msg)
        return redirect('accounts:register')

    # save details
    new_user.set_password(password)
    new_user.save()

    messages.success(request, 'User successfully registered')

    return redirect('accounts:login')
