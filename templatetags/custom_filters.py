
import re
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

from medicines.models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {
        'unread_notification_count': unread_count
    }