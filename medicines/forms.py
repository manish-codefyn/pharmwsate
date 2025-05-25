from django import forms
from .models import Medicine, DonationRequest, Category
from django.core.exceptions import ValidationError
from django.utils import timezone

from django import forms
from .models import MedicineRequest,DeliveryAddress
from django.contrib.auth import get_user_model
User = get_user_model()



class MedicineRequestForm(forms.ModelForm):
    class Meta:
        model = MedicineRequest
        fields = ['quantity_requested', 'message']
        widgets = {
            'quantity_requested': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Enter quantity needed',
                'required': 'required'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional information (optional)'
            }),
        }

class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'is_primary']
        widgets = {
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address, P.O. box, company name',
                'required': 'required'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, unit, building, floor, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': 'required'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province/Region',
                'required': 'required'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal code',
                'required': 'required'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country',
                'required': 'required'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'category', 'quantity', 'expiry_date', 'image']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date < timezone.now().date():
            raise ValidationError("Expiry date cannot be in the past.")
        return expiry_date

class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ['quantity_requested', 'purpose']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']