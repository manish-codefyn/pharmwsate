# medicines_dashboard/urls.py
from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('medicines/', views.MedicineListView.as_view(), name='medicine-list'),
    path('medicines/<uuid:pk>/request/', views.RequestCreateView.as_view(), name='request-create'),
    path('requests/', views.RequestListView.as_view(), name='request-list'),
    path('requests/<uuid:pk>/', views.RequestDetailView.as_view(), name='request-detail'),
    path('requests/<uuid:pk>/update/', views.RequestUpdateView.as_view(), name='request-update'),
    path('my-requests/', views.MyRequestListView.as_view(), name='my-requests'),
]