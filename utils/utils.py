from datetime import date, timedelta
from django.db.models import Count, Q
from django.urls import reverse

from medicines.models import Medicine, Category
from notifications.models import Notification  # Assuming your Notification model is here

def get_expiring_medicines(days=30):
    """Return medicines expiring within the specified number of days"""
    threshold_date = date.today() + timedelta(days=days)
    return Medicine.objects.filter(
        expiry_date__lte=threshold_date,
        expiry_date__gte=date.today(),
        is_available=True
    ).order_by('expiry_date')

def get_medicine_categories_with_counts():
    """Return categories with counts of available medicines"""
    return Category.objects.annotate(
        available_medicines=Count(
            'medicine',
            filter=Q(medicine__is_available=True) & Q(medicine__expiry_date__gte=date.today())
        )
    ).order_by('name')

def send_expiry_notifications():
    """Send notifications for medicines expiring soon"""
    expiring_soon = get_expiring_medicines(7)  # 7 days before expiry

    for medicine in expiring_soon:
        Notification.objects.create(
            user=medicine.donor,
            message=f"Your medicine '{medicine.name}' is expiring on {medicine.expiry_date}.",
            related_url=reverse('medicines:medicine-detail', kwargs={'slug': medicine.slug})
        )
