import uuid
from django.db import models

from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse

from django.conf import settings
from utils.email_utils import send_medicine_request_status_email, send_medicine_request_creation_email

from django.contrib.auth import get_user_model
User = get_user_model()



class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name



class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    expiry_date = models.DateField()
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donated_medicines')
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_medicines')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:6]}")
        
        # Check if medicine is expired
        if self.expiry_date < timezone.now().date():
            self.is_available = False
            
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    def get_absolute_url(self):
        return reverse('medicines:medicine-detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"{self.name} (Exp: {self.expiry_date})"



class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Request for {self.medicine.name} by {self.requester.username}"



class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}"
    

class DeliveryAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}"



class MedicineRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medicine_requests')
    quantity_requested = models.PositiveIntegerField()
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Medicine Request'
        verbose_name_plural = 'Medicine Requests'

    def __str__(self):
        return f"Request #{self.id} for {self.medicine.name}"

    def save(self, *args, **kwargs):
        # Check if this is a new request
        is_new = self._state.adding
        
        # Handle status changes and timestamps
        if self.status == self.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == self.SHIPPED and not self.shipped_at:
            self.shipped_at = timezone.now()
        elif self.status == self.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Send emails after save to ensure we have an ID
        if is_new:
            # New request - send creation emails
            send_medicine_request_creation_email(self)
        else:
            # Existing request - check if status changed
            if 'status' in kwargs.get('update_fields', []) or 'status' in kwargs:
                # Status changed - send notification emails
                send_medicine_request_status_email(self)  # to user
                send_medicine_request_status_email(self, to_admin=True)  # to admin