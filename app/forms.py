from django import forms
from .models import MaintenanceRequest
from .widgets import CustomClearableFileInput


class MaintenanceRequestForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100, 
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-control'})
        )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter primary tenant's email", 'class': 'form-control'})
        )
    subject = forms.CharField(
        max_length=200,
        label="Subject",
        widget=forms.TextInput(attrs={'placeholder': 'Enter maintenance issue', 'class': 'form-control'})
        )
    message = forms.CharField(
        max_length=500,  
        label='Message',
        widget=forms.Textarea(attrs={
            'placeholder': "Message",
            'class': 'form-control',
            'maxlength': 500  
        })
    )
    images = forms.FileField(
        widget=CustomClearableFileInput(attrs={'multiple': True}),
        required=False,
        label="Attach Images",
    )
    availability = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Monday - Friday 3PM - 6PM'}),
        label="Availability"
        )

    class Meta:
        model = MaintenanceRequest
        fields = ['full_name', 'email', 'subject', 'message', 'images', 'availability']
