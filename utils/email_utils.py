# utils/email_utils.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from io import BytesIO
from xhtml2pdf import pisa
from django.utils import timezone

def send_medicine_request_status_email(request_obj, to_admin=False):
    """
    Send email notification for medicine request status change
    """
    subject = f"Medicine Request #{request_obj.id} - Status Update"
    
    # Determine recipient and context
    if to_admin:
        recipient_email = settings.ADMIN_EMAIL
        template = 'emails/medicine_request_status_admin.html'
    else:
        recipient_email = request_obj.requester.email
        template = 'emails/medicine_request_status_user.html'
    
    context = {
        'request': request_obj,
        'status': request_obj.get_status_display(),
        'current_date': timezone.now().strftime("%d %b, %Y"),
    }
    
    # Render HTML content
    html_content = render_to_string(template, context)
    
    # Generate PDF
    pdf_content = render_to_string('emails/medicine_request_pdf.html', context)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(pdf_content, dest=pdf_buffer)
    
    # Create email
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.content_subtype = "html"
    
    # Attach PDF
    email.attach(
        filename=f"Medicine_Request_{request_obj.id}.pdf",
        content=pdf_buffer.getvalue(),
        mimetype="application/pdf"
    )
    
    # Send email
    email.send()


def send_medicine_request_creation_email(request_obj):
    """
    Send email notification when a new medicine request is created
    """
    # Email to user
    user_subject = f"Medicine Request #{request_obj.id} - Confirmation"
    user_context = {
        'request': request_obj,
        'current_date': timezone.now().strftime("%d %b, %Y"),
    }
    
    user_html_content = render_to_string(
        'emails/medicine_request_created_user.html', 
        user_context
    )
    
    # Email to admin
    admin_subject = f"New Medicine Request #{request_obj.id} - Approval Needed"
    admin_context = {
        'request': request_obj,
        'current_date': timezone.now().strftime("%d %b, %Y"),
    }
    
    admin_html_content = render_to_string(
        'emails/medicine_request_created_admin.html', 
        admin_context
    )
    
    # Generate PDF for both
    pdf_content = render_to_string('emails/medicine_request_pdf.html', user_context)
    pdf_buffer = BytesIO()
    pisa.CreatePDF(pdf_content, dest=pdf_buffer)
    pdf_data = pdf_buffer.getvalue()
    
    # Send user email
    user_email = EmailMessage(
        subject=user_subject,
        body=user_html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[request_obj.requester.email],
    )
    user_email.content_subtype = "html"
    user_email.attach(
        filename=f"Medicine_Request_{request_obj.id}.pdf",
        content=pdf_data,
        mimetype="application/pdf"
    )
    user_email.send()
    
    # Send admin email
    admin_email = EmailMessage(
        subject=admin_subject,
        body=admin_html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL],
    )
    admin_email.content_subtype = "html"
    admin_email.attach(
        filename=f"Medicine_Request_{request_obj.id}.pdf",
        content=pdf_data,
        mimetype="application/pdf"
    )
    admin_email.send()