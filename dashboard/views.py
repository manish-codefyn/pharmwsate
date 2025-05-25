# medicines_dashboard/views.py
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404,redirect
from medicines.models import Medicine, MedicineRequest
from medicines.forms import MedicineRequestForm

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/dashboard.html'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return MedicineRequest.objects.all().order_by('-created_at')[:5]
        return MedicineRequest.objects.filter(
            requester=self.request.user
        ).order_by('-created_at')[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_medicines'] = Medicine.objects.filter(is_available=True).count()
        context['is_admin'] = self.request.user.is_staff
        return context

class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = 'dashboard/medicine_list.html'
    context_object_name = 'medicines'
    
    def get_queryset(self):
        return Medicine.objects.filter(is_available=True)

class RequestCreateView(LoginRequiredMixin, CreateView):
    model = MedicineRequest
    form_class = MedicineRequestForm
    template_name = 'dashboard/request_create.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard:my-requests')
    
    def get_initial(self):
        medicine = get_object_or_404(Medicine, pk=self.kwargs['pk'])
        return {
            'medicine': medicine,
            'quantity_requested': 1
        }
    
    def form_valid(self, form):
        form.instance.requester = self.request.user
        form.instance.medicine = get_object_or_404(Medicine, pk=self.kwargs['pk'])
        return super().form_valid(form)

class RequestListView(LoginRequiredMixin, ListView):
    model = MedicineRequest
    template_name = 'dashboard/request_list.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return MedicineRequest.objects.all().order_by('-created_at')
        return MedicineRequest.objects.none()  # Regular users shouldn't access this
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard:my-requests')
        return super().dispatch(request, *args, **kwargs)

class MyRequestListView(LoginRequiredMixin, ListView):
    model = MedicineRequest
    template_name = 'dashboard/my_requests.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        return MedicineRequest.objects.filter(
            requester=self.request.user
        ).order_by('-created_at')

class RequestDetailView(LoginRequiredMixin, DetailView):
    model = MedicineRequest
    template_name = 'dashboard/request_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_staff and obj.requester != request.user:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

class RequestUpdateView(LoginRequiredMixin, UpdateView):
    model = MedicineRequest
    fields = ['status']
    template_name = 'dashboard/request_update.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('dashboard:request-detail', kwargs={'pk': self.object.pk})