from django.urls import path
from .views import (
    HomeView, MedicineListView, MedicineDetailView, MedicineCreateView,
    MedicineUpdateView, MedicineDeleteView, DonorDashboardView,
    RecipientDashboardView, create_donation_request, update_donation_request_status,
    CategoryListView, CategoryCreateView, mark_notification_as_read,NotificationListView,MarkAllNotificationsReadView, create_medicine_request,create_delivery_address_ajax)

app_name = 'medicines'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('medicines/', MedicineListView.as_view(), name='medicine-list'),
 
    path('medicines/add/', MedicineCreateView.as_view(), name='medicine-create'),
    path('medicines/<slug:slug>/edit/', MedicineUpdateView.as_view(), name='medicine-update'),
    path('medicines/<slug:slug>/delete/', MedicineDeleteView.as_view(), name='medicine-delete'),
    path('medicines/<slug:slug>/', MedicineDetailView.as_view(), name='medicine-detail'),
    path('donor-dashboard/', DonorDashboardView.as_view(), name='donor-dashboard'),
    path('recipient-dashboard/', RecipientDashboardView.as_view(), name='recipient-dashboard'),



   path('medicine/<slug:slug>/request/', create_medicine_request, name='medicine-request'),
    path('create-delivery-address/', create_delivery_address_ajax, name='create-delivery-address'),
    path('medicines/<slug:slug>/request/', create_donation_request, name='donation-request-create'),
    path('donation-requests/<uuid:pk>/<str:status>/', update_donation_request_status, name='update-request-status'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category-create'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/<uuid:pk>', mark_notification_as_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark-all-notification-read'),

]