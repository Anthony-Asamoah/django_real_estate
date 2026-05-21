import pendulum
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import HttpResponse, redirect
from django.template.loader import render_to_string
from wagtail.models import Site

from .models import GeneralInquiry, ProjectInquiry, EmailSettings


def _get_email_settings(request):
    site = Site.find_for_request(request)
    return EmailSettings.for_site(site)


def contact(request):
    if request.method == 'POST':
        listing_id = request.POST['listing_id']
        user_id = request.POST['user_id']
        listing = request.POST['listing']
        email = request.POST['email']

        if request.user.is_authenticated:
            user_id = request.user.id
            contacted = ProjectInquiry.objects.filter(listing_id=listing_id, user_id=user_id)
            if contacted:
                messages.error(request, 'You have already inquired about this project.')
                return redirect('projects:projects')

        new_contact = ProjectInquiry(
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

        settings = _get_email_settings(request)
        subject = settings.project_inquiry_subject
        intro = settings.project_inquiry_intro.format(project=listing)
        site_name = settings.site.site_name

        html_body = render_to_string('emails/project_inquiry.html', {
            'subject': subject,
            'intro': intro,
            'site_name': site_name,
            'project': listing,
            'name': new_contact.name,
            'email': new_contact.email,
            'phone': new_contact.phone,
            'message': new_contact.message,
        })

        msg = EmailMultiAlternatives(subject, intro, 'anthonyasamoah48@gmail.com', [email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)

        messages.success(request, 'Your inquiry has been received. We will get back to you shortly.')
        return redirect('projects:projects')

    return HttpResponse('request: GET')


def general_inquiry(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not email and not phone:
            messages.error(request, 'Please provide at least an email address or phone number.')
            return redirect('/contact/')

        inquiry = GeneralInquiry(
            name=request.POST.get('name', ''),
            email=email,
            phone=phone,
            service=request.POST.get('service', ''),
            message=request.POST.get('message', ''),
            timestamp=pendulum.now(),
        )
        inquiry.save()

        if email:
            settings = _get_email_settings(request)
            subject = settings.general_inquiry_subject
            intro = settings.general_inquiry_intro.format(name=inquiry.name)
            site_name = settings.site.site_name

            html_body = render_to_string('emails/general_inquiry.html', {
                'subject': subject,
                'intro': intro,
                'site_name': site_name,
                'name': inquiry.name,
                'email': inquiry.email,
                'phone': inquiry.phone,
                'service': inquiry.service,
                'message': inquiry.message,
            })

            msg = EmailMultiAlternatives(subject, intro, 'anthonyasamoah48@gmail.com', [email])
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)

        messages.success(request, 'Thank you! We will be in touch shortly.')
        return redirect('/contact/')

    return redirect('/contact/')
