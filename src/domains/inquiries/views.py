import pendulum
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from wagtail.models import Site

from domains.pages.models import BrandingSettings, Testimonial
from infrastructure.email import get_email_provider
from infrastructure import recaptcha
from .models import GeneralInquiry, ProjectInquiry, EmailSettings

_MODEL_MAP = None


def _get_model_map():
    global _MODEL_MAP
    if _MODEL_MAP is None:
        _MODEL_MAP = {
            'project': ProjectInquiry,
            'general': GeneralInquiry,
            'testimonial': Testimonial,
        }
    return _MODEL_MAP


def notification_counts(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)
    return JsonResponse({
        'project': ProjectInquiry.objects.filter(is_read=False).count(),
        'general': GeneralInquiry.objects.filter(is_read=False).count(),
        'testimonial': Testimonial.objects.filter(is_read=False).count(),
    })


@require_POST
def mark_read(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)

    model_name = request.POST.get('model')
    pk = request.POST.get('pk', '').strip()
    model_cls = _get_model_map().get(model_name)

    if not model_cls:
        return JsonResponse({'error': 'invalid model'}, status=400)

    qs = model_cls.objects.filter(is_read=False)
    if pk:
        qs = qs.filter(pk=pk)
    qs.update(is_read=True)

    return JsonResponse({'ok': True, 'remaining': model_cls.objects.filter(is_read=False).count()})


def _get_site_context(request):
    site = Site.find_for_request(request)
    email_settings = EmailSettings.for_site(site)
    branding = BrandingSettings.for_site(site)
    return email_settings, branding.site_name


def contact(request):
    if request.method == 'POST':
        if not recaptcha.verify(request.POST.get('g-recaptcha-response', ''), 'project_inquiry'):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return redirect('projects:projects')

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

        settings, site_name = _get_site_context(request)
        subject = settings.project_inquiry_subject
        intro = settings.project_inquiry_intro.format(project=listing)

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

        get_email_provider().send(email, subject, intro, html_body)

        messages.success(request, 'Your inquiry has been received. We will get back to you shortly.')
        return redirect('projects:projects')

    return HttpResponse('request: GET')


def general_inquiry(request):
    if request.method == 'POST':
        if not recaptcha.verify(request.POST.get('g-recaptcha-response', ''), 'contact'):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return redirect('/contact/')

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
            settings, site_name = _get_site_context(request)
            subject = settings.general_inquiry_subject
            intro = settings.general_inquiry_intro.format(name=inquiry.name)

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

            get_email_provider().send(email, subject, intro, html_body)

        messages.success(request, 'Thank you! We will be in touch shortly.')
        return redirect('/contact/')

    return redirect('/contact/')


def testimonial_submission(request):
    if request.method == 'POST':
        if not recaptcha.verify(request.POST.get('g-recaptcha-response', ''), 'testimonial'):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return redirect('/projects/')

        author_name = request.POST.get('author_name', '').strip()
        body = request.POST.get('body', '').strip()

        if not author_name or not body:
            messages.error(request, 'Please provide your name and a testimonial.')
            return redirect('/projects/')

        Testimonial(
            author_name=author_name,
            author_role=request.POST.get('author_role', '').strip(),
            body=body,
            is_featured=False,
        ).save()

        messages.success(request, 'Thank you for your testimonial! We will review it shortly.')
        return redirect('/projects/')

    return redirect('/projects/')
