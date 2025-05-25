from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Medicine, DonationRequest, Category, Notification,MedicineRequest,DeliveryAddress
from .forms import MedicineForm, DonationRequestForm, CategoryForm,MedicineRequestForm,DeliveryAddressForm
import uuid
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

@login_required
def request_detail(request, id):
    medicine_request = get_object_or_404(MedicineRequest, id=id, requester=request.user)
    
    context = {
        'request': medicine_request,
    }
    return render(request, 'medicines/request_detail.html', context)


@login_required
def create_medicine_request(request, slug):
    medicine = get_object_or_404(Medicine, slug=slug)
    user_addresses = request.user.delivery_addresses.all()
    
    if request.method == 'POST':
        # Determine which address option was selected
        address_option = request.POST.get('address_option', 'new')
        
        if address_option == 'existing':
            # Handle existing address selection
            request_form = MedicineRequestForm(request.POST)
            selected_address_id = request.POST.get('existing_address')
            
            if selected_address_id:
                delivery_address = get_object_or_404(DeliveryAddress, id=selected_address_id, user=request.user)
                medicine_request = MedicineRequest(
                    medicine=medicine,
                    requester=request.user,
                    quantity_requested=request.POST.get('quantity_requested'),
                    message=request.POST.get('message'),
                    delivery_address=delivery_address,
                    status='pending'
                )
                medicine_request.save()
                messages.success(request, 'Medicine request submitted successfully!')
                return redirect('medicines:medicine-detail', slug=medicine.slug)
            else:
                messages.error(request, 'Please select an existing address')
        
        else:  # address_option == 'new'
            # Handle new address creation
            request_form = MedicineRequestForm(request.POST)
            address_form = DeliveryAddressForm(request.POST)
            
            if address_form.is_valid():
                # Save new address
                delivery_address = address_form.save(commit=False)
                delivery_address.user = request.user
                
                # Handle primary address setting
                if address_form.cleaned_data.get('is_primary'):
                    DeliveryAddress.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
                
                delivery_address.save()
                
                # Save medicine request
                medicine_request = MedicineRequest(
                    medicine=medicine,
                    requester=request.user,
                    quantity_requested=request.POST.get('quantity_requested'),
                    message=request.POST.get('message'),
                    delivery_address=delivery_address,
                    status='pending'
                )
                medicine_request.save()
                
                messages.success(request, 'Medicine request submitted successfully!')
                return redirect('medicines:medicine-detail', slug=medicine.slug)
            else:
                messages.error(request, 'Please correct the errors in the address form')
    else:
        request_form = MedicineRequestForm()
        address_form = DeliveryAddressForm()
    
    context = {
        'medicine': medicine,
        'request_form': request_form,
        'address_form':  DeliveryAddressForm(),
        'user_addresses': user_addresses,
    }
    return render(request, 'medicines/medicine_request_form.html', context)

@login_required
@require_http_methods(["POST"])
def create_delivery_address_ajax(request):
    form = DeliveryAddressForm(request.POST)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        
        # Set as primary if requested
        if form.cleaned_data.get('is_primary'):
            DeliveryAddress.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        
        address.save()
        
        return JsonResponse({
            'success': True,
            'address_id': address.id,
            'address_display': f"{address.address_line1}, {address.city}, {address.state}",
            'message': 'Address saved successfully!'
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors,
        'message': 'Please correct the errors below.'
    }, status=400)

# class MedicineRequestView(LoginRequiredMixin, CreateView):
#     model = MedicineRequest
#     form_class = MedicineRequestForm
#     template_name = 'medicines/medicine_request_form.html'
#     login_url = reverse_lazy('login')  # Redirect to login page if not authenticated

#     def dispatch(self, request, *args, **kwargs):
#         self.medicine = get_object_or_404(Medicine, pk=self.kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         form.instance.medicine = self.medicine
#         messages.success(self.request, "Your medicine request has been submitted successfully.")
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['medicine'] = self.medicine
#         return context

#     def get_success_url(self):
#         return self.medicine.get_absolute_url()  # Or customize as needed



class HomeView(ListView):
    model = Medicine
    template_name = 'medicines/home.html'
    context_object_name = 'medicines'
    paginate_by = 10
    
    def get_queryset(self):
        return Medicine.objects.filter(
            is_available=True,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date')


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect(request.META.get('HTTP_REFERER', 'medicines:notifications'))  #
    


class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = 'medicines/medicine_list.html'
    context_object_name = 'medicines'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset.filter(
            is_available=True,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    

class MedicineDetailView(LoginRequiredMixin, DetailView):
    model = Medicine
    template_name = 'medicines/medicine_detail.html'
    context_object_name = 'medicine'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


class MedicineCreateView(LoginRequiredMixin, CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/medicine_create.html'
    
    def form_valid(self, form):
        form.instance.donor = self.request.user
        return super().form_valid(form)


class MedicineUpdateView(LoginRequiredMixin, UpdateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/medicine_update.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.donor != self.request.user:
            messages.error(request, "You don't have permission to edit this medicine.")
            return redirect(obj)
        return super().dispatch(request, *args, **kwargs)

class MedicineDeleteView(LoginRequiredMixin, DeleteView):
    model = Medicine
    template_name = 'medicines/medicine_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('medicine-list')
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.donor != self.request.user:
            messages.error(request, "You don't have permission to delete this medicine.")
            return redirect(obj)
        return super().dispatch(request, *args, **kwargs)

class DonorDashboardView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = 'medicines/donor_dashboard.html'
    context_object_name = 'medicines'
    
    def get_queryset(self):
        return Medicine.objects.filter(donor=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['donation_requests'] = DonationRequest.objects.filter(
            medicine__donor=self.request.user
        ).order_by('-created_at')
        return context

class RecipientDashboardView(LoginRequiredMixin, ListView):
    model = DonationRequest
    template_name = 'medicines/recipient_dashboard.html'
    context_object_name = 'donation_requests'
    
    def get_queryset(self):
        return DonationRequest.objects.filter(requester=self.request.user).order_by('-created_at')

def create_donation_request(request, slug):
    medicine = get_object_or_404(Medicine, slug=slug, is_available=True)
    
    if request.method == 'POST':
        form = DonationRequestForm(request.POST)
        if form.is_valid():
            donation_request = form.save(commit=False)
            donation_request.medicine = medicine
            donation_request.requester = request.user
            
            if donation_request.quantity_requested > medicine.quantity:
                messages.error(request, "Requested quantity exceeds available quantity.")
            else:
                donation_request.save()
                
                # Create notification for donor
                Notification.objects.create(
                    user=medicine.donor,
                    message=f"{request.user.username} has requested {donation_request.quantity_requested} units of {medicine.name}.",
                    related_url=reverse_lazy('medicines:donor-dashboard')
                )
                
                messages.success(request, "Donation request submitted successfully!")
                return redirect('medicines:medicine-detail', slug=medicine.slug)
    else:
        form = DonationRequestForm()
    
    return render(request, 'medicines/donation_request_create.html', {
        'form': form,
        'medicine': medicine
    })

def update_donation_request_status(request, pk, status):
    donation_request = get_object_or_404(DonationRequest, pk=pk)
    
    if donation_request.medicine.donor != request.user:
        messages.error(request, "You don't have permission to update this request.")
        return redirect('donor-dashboard')
    
    if status not in ['approved', 'rejected', 'completed']:
        messages.error(request, "Invalid status.")
        return redirect('donor-dashboard')
    
    donation_request.status = status
    donation_request.save()
    
    # Update medicine quantity if approved or completed
    if status == 'approved' or status == 'completed':
        medicine = donation_request.medicine
        if donation_request.quantity_requested <= medicine.quantity:
            medicine.quantity -= donation_request.quantity_requested
            if medicine.quantity == 0:
                medicine.is_available = False
            medicine.save()
            
            if status == 'completed':
                donation_request.recipient = donation_request.requester
                donation_request.save()
    
    # Create notification for requester
    Notification.objects.create(
        user=donation_request.requester,
        message=f"Your request for {donation_request.medicine.name} has been {status}.",
        related_url=reverse_lazy('recipient-dashboard')
    )
    
    messages.success(request, f"Request has been {status}.")
    return redirect('donor-dashboard')

class CategoryListView(ListView):
    model = Category
    template_name = 'medicines/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'medicines/category_create.html'
    success_url = reverse_lazy('category-list')

def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.related_url if notification.related_url else 'home')

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'medicines/notifications.html'
    context_object_name = 'notifications'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')