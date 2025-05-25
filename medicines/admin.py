from django.contrib import admin
from .models import Category, Medicine, DonationRequest, Notification,  MedicineRequest, DeliveryAddress

@admin.register(MedicineRequest)
class MedicineRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'medicine', 'quantity_requested', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('medicine__name', 'requester__username')
    readonly_fields = ('approved_at', 'shipped_at', 'delivered_at', 'created_at', 'updated_at')

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'state', 'postal_code', 'country', 'is_primary')
    list_filter = ('city', 'state', 'country', 'is_primary')
    search_fields = ('user__username', 'address_line1', 'city', 'state')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'expiry_date', 'is_available')
    list_filter = ('category', 'is_available', 'expiry_date')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'requester', 'quantity_requested', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('medicine__name', 'requester__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
