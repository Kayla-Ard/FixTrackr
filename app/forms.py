from django import forms
from .models import MaintenanceRequest
# from .widgets import CustomClearableFileInput




class MaintenanceRequestForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-control'}),
        error_messages={'required': 'Please enter full name'}
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter primary tenant's email", 'class': 'form-control'}),
        error_messages={'required': "Please enter primary tenant's email"}
    )
    subject = forms.CharField(
        max_length=200,
        label="Subject",
        widget=forms.TextInput(attrs={'placeholder': 'Enter maintenance issue', 'class': 'form-control'}),
        error_messages={'required': "Please enter subject line for maintenance issue"}
    )
    tenant_message = forms.CharField(
        max_length=500,
        label='Message',
        widget=forms.Textarea(attrs={
            'placeholder': "Message",
            'class': 'form-control',
            'maxlength': 500
        }),
        error_messages={'required': "Please enter a message for your property manager"}
    )
    images = forms.FileField(
        widget=forms.ClearableFileInput(),
        required=False,
        label="Attach Image",
    )
    availability = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Monday - Friday 3PM - 6PM'}),
        label="Availability",
        error_messages={'required': 'Please enter your availability or enter "N/A"'}
    )

    class Meta:
        model = MaintenanceRequest
        fields = ['full_name', 'email', 'subject', 'tenant_message', 'images', 'availability']
        