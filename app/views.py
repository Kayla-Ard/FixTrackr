from django.http import JsonResponse, HttpResponseServerError
from django.template import loader
from .models import Property_Manager, MaintenanceRequest, Image, Tenant, Unit, Notification
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import render, get_object_or_404, redirect
from .forms import MaintenanceRequestForm
import uuid
from .serializers import *
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
import json

def customizeError(errors):
    errorsDict = {}
    for key in errors:
        if key == 'non_field_errors':
            errorsDict['error'] = errors[key][0]
        else:
            errorsDict[key] = errors[key][0] if type(errors[key]) == list else errors[key]
    return errorsDict

class RegisterPropertyManager(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny,]
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status = status.HTTP_201_CREATED)
        else:
            return Response(customizeError(serializer.errors), status = status.HTTP_400_BAD_REQUEST)

class CreateUnit(APIView):
    serializer_class = RegisterUnitSerializer
    permission_classes = [permissions.IsAuthenticated,]
    def post(self,request):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny,]
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            return Response(serializer.data,status = status.HTTP_200_OK)
        else:
            return Response(customizeError(serializer.errors), status = status.HTTP_400_BAD_REQUEST)

class GetUnits(APIView):
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated,]
    def get(self,request):
        units = Unit.objects.filter(property_manager=request.user)
        serializer = self.serializer_class(units, many = True)
        data = {
            'property_manager': request.user.first_name + " " + request.user.last_name,
            'units': serializer.data
        }
        return Response(data,status = status.HTTP_200_OK)

class UnitsView(APIView):
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request,pk):
        try:
            unit = Unit.objects.get(pk = pk)
            serializer = self.serializer_class(unit, many = False)
            return Response(serializer.data,status = status.HTTP_200_OK)
        except Unit.DoesNotExist:
            return Response("Unit Not Found", status = status.HTTP_404_NOT_FOUND)

    def put(self,request,pk):
        try:
            unit = Unit.objects.get(pk = pk)
            serializer = self.serializer_class(unit, data = request.data,partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status = status.HTTP_200_OK)
            else:
                return Response(customizeError(serializer.errors),status = status.HTTP_400_BAD_REQUEST)
        except Unit.DoesNotExist:
            return Response("Unit Not Found", status = status.HTTP_404_NOT_FOUND)

class CreateMaintenanceRequest(APIView):
    serializer_class = NewMaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated,]
    def post(self,request):
        data = request.data.copy()
        files = request.FILES.getlist('images') or []
        data.setlist('images', files) 
        serializer = self.serializer_class(data=data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetMaintenanceRequests(APIView):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request):
        requests = MaintenanceRequest.objects.filter(property_manager=request.user)
        requests_serializer = self.serializer_class(requests, many = True)
        units = Unit.objects.filter(property_manager=request.user)
        units_serializer = UnitSerializer(units, many = True)
        data = {
            'units': units_serializer.data,
            'requests': requests_serializer.data
        }
        return Response(data,status = status.HTTP_200_OK)

class GetNotifications(APIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request):
        notifications = Notification.objects.filter(property_manager=request.user).order_by('-created_at')
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class ReadNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def put(self,request,pk):
        try:
            notification = Notification.objects.get(pk=pk)
            notification.read = True
            notification.save()
            if MaintenanceRequest.objects.filter(pk = notification.maintenance_request.pk).exists():
                maintenance_request = MaintenanceRequest.objects.get(pk = notification.maintenance_request.pk)
                maintenance_request.status = "Request Read"
                maintenance_request.save()
                # Generate the URL to the tenant's specific progress check page
                progress_check_url = request.build_absolute_uri(reverse('progress_check', kwargs={'request_number': maintenance_request.request_number}))
                # Send an email notification to the tenant
                tenant_email = maintenance_request.email
                send_mail(
                    subject="Your Maintenance Request Has Been Read",
                    message=f"Hello {maintenance_request.full_name},\n\nYour maintenance request with the subject '{maintenance_request.subject}' has been read by your property manager.\n\n You can track the progress of your request directly using the link below:\n\n{progress_check_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[tenant_email],
                    fail_silently=False,
                )
                return Response({"message": "Request marked as read and tenant notified"}, status=status.HTTP_200_OK)
            else:
                return Response("MAINTENANCE NOT FOUND", status = status.HTTP_404_NOT_FOUND)
        except Tenant.DoesNotExist:
            return Response("NOTIFICATION NOT FOUND", status = status.HTTP_404_NOT_FOUND)

class GetMaintenanceRequest(APIView):
    serializer_class = RequestDetailSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self,request,pk):
        try:
            request = MaintenanceRequest.objects.get(pk = pk)
            serializer = self.serializer_class(request, many = False)
            return Response(serializer.data,status = status.HTTP_200_OK)
        except Unit.DoesNotExist:
            return Response("Maintenance Not Found", status = status.HTTP_404_NOT_FOUND)

class EditMaintenanceRequest(APIView):
    serializer_class = RequestUpdateSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def put(self,request,pk):
        try:
            maintenance_instance = MaintenanceRequest.objects.get(pk = pk)
            data = request.data.copy()
            files = request.FILES.getlist('new_files') or []
            data.setlist('new_files', files)
            serializer = self.serializer_class(maintenance_instance, data = request.data,partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status = status.HTTP_200_OK)
            else:
                return Response(customizeError(serializer.errors), status = status.HTTP_400_BAD_REQUEST)
        except Unit.DoesNotExist:
            return Response("Maintenance Not Found", status = status.HTTP_404_NOT_FOUND)

# Tenant related HTML Views

def tenant_home(request):
    return render(request, 'tenant_home.html')


def generate_request_number():
    return str(uuid.uuid4()).split('-')[0].upper()


def submit_request(request):
    if request.method == 'POST':
        print("Received POST request")
        form = MaintenanceRequestForm(request.POST, request.FILES)
        print("FILES:", request.FILES)
        if form.is_valid():
            print("Form is valid")
            maintenance_request = form.save(commit=False)
            maintenance_request.date_sent = timezone.now()
            maintenance_request.request_number = generate_request_number()            
            try:
                tenant = Tenant.objects.get(email=maintenance_request.email)
                maintenance_request.property_manager = tenant.unit.property_manager
                maintenance_request.unit = tenant.unit
                print(f"Found tenant: {tenant.full_name}")
                # Get the unit associated with the tenant
                print(f"Found unit title: ")
            except Tenant.DoesNotExist:
                print("Tenant not found")
                return render(request, 'submit_request.html', {'form': form, 'error': 'Tenant not found'})
            
            try:
                maintenance_request.save()
                print("Maintenance request saved")

                if 'images' in request.FILES:
                    print("Processing images")
                    for image_file in  request.FILES.getlist('images'):
                        image = Image(file=image_file, maintenance_request=maintenance_request)
                        image.save()
                        print(f"Saved image: {image_file.name}")
                
                
                # Create a notification for the property manager
                Notification.objects.create(
                    property_manager=maintenance_request.property_manager,
                    maintenance_request=maintenance_request,
                    message=f"You have a new maintenance request from {maintenance_request.full_name}.",
                    unit=tenant.unit, # The unit title from the tenant's unit
                    tenant = tenant
                )
                print("Notification created")
                
                # Use reverse to construct the URL correctly
                url = reverse('request_submitted', args=[maintenance_request.request_number])
                print(f"Redirecting to {url}")
                return redirect(url)
                
            except Exception as e:
                print(f"Error occurred while saving maintenance request: {e}")
                return render(request, 'submit_request.html', {'form': form, 'error': 'An error occurred while saving the request'})
        else:
            print(form.errors)
            return render(request, 'submit_request.html', {'form': form, 'errors': form.errors})
    else:
        form = MaintenanceRequestForm()
    return render(request, 'submit_request.html', {'form': form})

def request_submitted(request, request_number=None):
    context = {
        'request_number': request_number
    }
    return render(request, 'request_submitted.html', context)

 
def check_request_status(request):
    error_message = None  

    if request.method == 'POST':
        request_number = request.POST.get('request_number').strip().upper()
        print(f"Received request number: {request_number}")
        
        if not request_number:
            error_message = "Please enter a request number."
            print(f"Error: {error_message}")
            
        try:
            # Validate if the request number exists in the database
            print("Maintenance Requests = ",[m.request_number for m in MaintenanceRequest.objects.all()])
            maintenance_request = MaintenanceRequest.objects.filter(request_number=request_number).first()
            print(f"Maintenance request found: {maintenance_request}")
            
            if not maintenance_request:
                error_message = "Request number not found. Please try again."
                print(f"Error: {error_message}")
                
            else:
                url = reverse('progress_check', args=[request_number])
                print("Redirecting to URL:", url)
                return redirect(url)
            
        except Exception as e:
            print(f"Error occurred during the request status check: {e}")
            error_message = "An unexpected error occurred. Please try again."
            
    # If the method is GET or the request number is invalid, render the form with any error message
    return render(request, 'check_request_status.html', {'error_message': error_message})




def validate_request_number(request_number):
    # Replace this with your actual validation logic
    valid_request_numbers = ['ABC0001', 'ABC0002']  # Example list of valid numbers
    return request_number in valid_request_numbers




def progress_check(request, request_number=None):
    try:
        if request_number:
            maintenance_request = get_object_or_404(MaintenanceRequest, request_number=request_number)
            print(f"Found maintenance request: {maintenance_request}")
        else:
            
            maintenance_request = None
        
        # Safely handle the property_manager
        property_manager_name = (
            f"{maintenance_request.property_manager.first_name} {maintenance_request.property_manager.last_name}"
            if maintenance_request and maintenance_request.property_manager 
            else 'N/A'
        )
        print(f"Property Manager: {property_manager_name}")
        
        statuses = ['Request Sent', 'Request Read', 'Contractor Called', 'Appointment Set', 'Request Complete']


        # Safely handle cases where the status might not be in the list
        current_index = -1
        if maintenance_request:
            if maintenance_request.status in statuses:
                current_index = statuses.index(maintenance_request.status)
                print(f"Current index of status '{maintenance_request.status}': {current_index}")
            else:
                print(f"Status '{maintenance_request.status}' not found in predefined statuses.")
        
        # Print out everything being sent to the template

        context = {
            'maintenance_request': maintenance_request,
            'statuses': statuses,
            'current_index': current_index,
            'property_manager_name': property_manager_name,
            'contractor_name': maintenance_request.contractor_name or '', 
            'contractor_phone': maintenance_request.contractor_phone or '',
            'property_manager_message': maintenance_request.property_manager_message or '',
        }
        # Print the entire context to help with debugging
        print("Context being sent to template:", context)
            
        return render(request, 'progress_check.html', context)
        
    except Exception as e:
        print(f"Error in progress_check view: {e}")
        return render(request, 'progress_check.html', {
            'error_message': 'An unexpected error occurred. Please try again later.',
        })