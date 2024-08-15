from django import forms
from .models import MaintenanceRequest
from .widgets import CustomClearableFileInput


class MaintenanceRequestForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100, 
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'John Smith', 'class': 'form-control'})
        )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Johnsmith@gmail.com', 'class': 'form-control'})
        )
    subject = forms.CharField(
        max_length=200,
        label="Subject",
        widget=forms.TextInput(attrs={'placeholder': 'Toilet Leak - Started Yesterday', 'class': 'form-control'})
        )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'placeholder': "The pipe connected to our toilet is starting to drip. I tried tightening it with a wrench but it didn't work. We need someone to come in ASAP.", 'class': 'form-control'})
        )
    image1 = forms.FileField(
        widget=CustomClearableFileInput(),
        required=False,
        label="Attach Image 1",
    )
    image2 = forms.FileField(
        widget=CustomClearableFileInput(),
        required=False,
        label="Attach Image 2",
    )
    image3 = forms.FileField(
        widget=CustomClearableFileInput(),
        required=False,
        label="Attach Image 3",
    )
    image4 = forms.FileField(
        widget=CustomClearableFileInput(),
        required=False,
        label="Attach Image 4",
    )
    availability = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Monday - Friday 3PM - 6PM'}),
        label="Availability"
        )

    class Meta:
        model = MaintenanceRequest
        fields = ['full_name', 'email', 'subject', 'message', 'image1', 'image2', 'image3', 'image4', 'availability']
