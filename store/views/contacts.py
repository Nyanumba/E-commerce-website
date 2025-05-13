# store/views.py
from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Contact(View):
    def get(self, request):
        return render(request, 'contacts.html')

    def post(self, request):
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not email or not message:
            return render(request, 'contacts.html', {
                'error': 'Please provide both email and message.'
            })

        try:
            logger.info(f"Attempting to send email from {email} to {settings.CONTACT_EMAIL}")
            # This line is where the error occurs
            send_mail(
                subject=f"New Contact Message from {email}",
                message=message,
                from_email=email,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            logger.info("Email sent successfully")
            return render(request, 'contacts.html', {
                'success': True
            })
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return render(request, 'contacts.html', {
                'error': f"Failed to send message: {str(e)}"
            })