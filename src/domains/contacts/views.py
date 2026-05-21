import pendulum
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import HttpResponse
from django.shortcuts import redirect

from .models import Contact, GeneralInquiry


# Create your views here.


def contact(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        user_id = request.POST['user_id']
        listing = request.POST['listing']
        email = request.POST['email']

        if request.user.is_authenticated:
            user_id = request.user.id
            contacted = Contact.objects.filter(listing_id=listing_id, user_id=user_id)
            if contacted:
                messages.error(request, 'You have already inquired about this project.')
                return redirect('projects:projects')

        new_contact = Contact(
            user_id=user_id,
            listing_id=listing_id,
            listing=listing,
            name=request.POST['name'],
            email=email,
            phone=request.POST['phone'],
            message=request.POST['message'],
            timestamp=pendulum.now()
        )
        new_contact.save()

        send_mail(
            'Real Estate Listing Inquiry',
            f'You have one new inquiry for {listing}.\n kindly sign in to find out more info.',
            'anthonyasamoah48@gmail.com',
            [email, ],
            fail_silently=False
        )

        messages.success(request, 'Your inquiry has been received. We will get back to you shortly.')

        return redirect('projects:projects')

    return HttpResponse('request: GET')


def general_inquiry(request):
    if request.method == 'POST':
        inquiry = GeneralInquiry(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            service=request.POST.get('service', ''),
            message=request.POST.get('message', ''),
            timestamp=pendulum.now(),
        )
        inquiry.save()

        send_mail(
            'New Inquiry',
            f'New inquiry from {inquiry.name} ({inquiry.email}).\nService: {inquiry.service or "General"}\n\n{inquiry.message}',
            'anthonyasamoah48@gmail.com',
            [inquiry.email],
            fail_silently=True,
        )

        messages.success(request, 'Thank you! We will be in touch shortly.')
        return redirect('/contact/')

    return redirect('/contact/')
