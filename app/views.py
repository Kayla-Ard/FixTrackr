
from django.http import HttpResponse
from django.template import loader
from .models import Property_Manager, MaintenanceRequest, Image, Tenant, Unit, UnitSerializer, Notification
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404, redirect
from .forms import MaintenanceRequestForm
import uuid
from .serializers import MaintenanceRequestSerializer, PropertyManagerSerializer
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





# Tenant related HTML Views

def tenant_home(request):
    return render(request, 'tenant_home.html')


def generate_request_number():
    return str(uuid.uuid4()).split('-')[0].upper()


def submit_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.date_sent = timezone.now()
            maintenance_request.request_number = generate_request_number()
            
            try:
                tenant = Tenant.objects.get(email=maintenance_request.email)
                maintenance_request.property_manager = tenant.property_manager
            except Tenant.DoesNotExist:
                return render(request, 'submit_request.html', {'form': form, 'error': 'Tenant not found'})
            
            maintenance_request.save()

            images = form.cleaned_data.get('images')
            if images:
                for image_file in images:
                    image = Image(file=image_file, maintenance_request=maintenance_request)
                    image.save()

            return render(request, 'request_submitted.html', {'request_number': maintenance_request.request_number})
        else:
            return render(request, 'submit_request.html', {'form': form})
    else:
        form = MaintenanceRequestForm()
    return render(request, 'submit_request.html', {'form': form})


def check_request_status(request):
    error_message = None  # Initialize the error message as None

    if request.method == 'POST':
        request_number = request.POST.get('request_number').strip()

        # Validate if the request number exists in the database
        maintenance_request = MaintenanceRequest.objects.filter(request_number=request_number).first()
        if not maintenance_request:
            error_message = "Request number not found. Please try again."
        else:
            # If the request number is valid, redirect to the progress check page
            return redirect('progress_check', request_number=request_number)

    # If the method is GET or the request number is invalid, render the form with any error message
    return render(request, 'check_request_status.html', {'error_message': error_message})




def validate_request_number(request_number):
    # Replace this with your actual validation logic
    valid_request_numbers = ['ABC0001', 'ABC0002']  # Example list of valid numbers
    return request_number in valid_request_numbers


def progress_check(request, request_number=None):
    if request_number:
        maintenance_request = get_object_or_404(MaintenanceRequest, request_number=request_number)
        print(f"Found maintenance request: {maintenance_request}")
    else:
        # Mock data for development purposes
        maintenance_request = {
            'request_number': 'ABC0001',
            'property_manager': {'name': 'John Doe'},
            'status': 'Request Sent',  
            'full_name': 'Jane Smith',
            'email': 'jane@example.com',
            'subject': 'Leaky faucet',
            'message': 'The kitchen faucet has been leaking for a week.',
        }
    
    # Safely handle the property_manager
    property_manager_name = maintenance_request.property_manager.name if maintenance_request and maintenance_request.property_manager else 'N/A'
    print(f"Property Manager: {property_manager_name}")
    
    statuses = ['Request<br>Sent', 'Request<br>Read', 'Contractor<br>Called', 'Appointment<br>Set', 'Request<br>Complete']

    # Safely handle cases where the status might not be in the list
    current_index = -1
    if maintenance_request:
        if maintenance_request.status in statuses:
            current_index = statuses.index(maintenance_request.status)
            print(f"Current index of status '{maintenance_request.status}': {current_index}")
        else:
            print(f"Status '{maintenance_request.status}' not found in predefined statuses.")

    return render(request, 'progress_check.html', {
        'maintenance_request': maintenance_request,
        'statuses': statuses,
        'current_index': current_index,
        'property_manager_name': property_manager_name,
        'contractor_name': maintenance_request.contractor_name or '', 
        'contractor_phone': maintenance_request.contractor_phone or '',
        'contractor_message': maintenance_request.contractor_message or '',
    })
    
# debugging output to see what files are being passed
def value_from_datadict(self, data, files, name):
    if isinstance(files, MultiValueDict):
        file_list = files.getlist(name)
        print(f"Files in widget value_from_datadict: {file_list}")  # Debugging line
        return file_list
    file = files.get(name, None)
    print(f"Single file in widget value_from_datadict: {file}")  # Debugging line
    return file









# PWA RESTful API endpoints

@api_view(['POST'])
def register_property_manager(request):
    data = request.data
    User = get_user_model()
    
    # Validate password match
    if data.get('password') != data.get('confirm_password'):
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate email uniqueness
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        print(f"User created: {user}")

        if not user:
            return Response({"error": "User creation failed"}, status=status.HTTP_400_BAD_REQUEST)

        # Create property manager
        property_manager = Property_Manager.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone')
        )

        # Create tenant records if provided
        tenants = data.get('tenants', [])
        for tenant in tenants:
            Tenant.objects.create(
                full_name=tenant['full_name'],
                email=tenant['email'],
                property_manager=property_manager
            )

        # Generate JWT tokens or perform login
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)







# Property manager login endpoint
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Normalize the email by converting it to lowercase and stripping any spaces
    email = email.lower().strip()
    print(f"Attempting to authenticate user with email: {email}")
    
    # Authenticate using the email and password
    user = authenticate(request, username=email, password=password)

    if user is not None:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)
    else:
        print(f"Authentication failed for email: {email}")
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)



# Create a unit
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_unit(request):
    data = request.data

    # Validate property manager existence
    try:
        property_manager = Property_Manager.objects.get(email=request.user.email)
    except Property_Manager.DoesNotExist:
        return Response({"error": "Property Manager not found."}, status=status.HTTP_400_BAD_REQUEST)

    # Create tenant and unit
    try:
        tenant = Tenant.objects.create(
            full_name=data.get('primary_tenant_name'),
            email=data.get('primary_tenant_email'),
            property_manager=property_manager
        )

        unit = Unit.objects.create(
            title=data.get('unit_title'),
            address=data.get('unit_address'),
            notes=data.get('notes', ''),
            tenant=tenant,
            property_manager=property_manager
        )

        return Response({
            "unit_id": unit.id,
            "title": unit.title,
            "address": unit.address,
            "primary_tenant_name": tenant.full_name,
            "primary_tenant_email": tenant.email,
            "notes": unit.notes,
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# List all units
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_units(request):
    property_manager = get_object_or_404(Property_Manager, email=request.user.email)
    units = Unit.objects.filter(property_manager=property_manager)
    serializer = UnitSerializer(units, many=True)
    return Response(serializer.data)




# Update a unit
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_unit(request, id):
    property_manager = get_object_or_404(Property_Manager, email=request.user.email)
    unit = get_object_or_404(Unit, id=id, property_manager=property_manager)

    serializer = UnitSerializer(unit, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Delete a unit
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_unit(request, id):
    property_manager = get_object_or_404(Property_Manager, email=request.user.email)
    unit = get_object_or_404(Unit, id=id, property_manager=property_manager)
    unit.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




# List notifications
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    try:
        # Get the Property_Manager instance for the authenticated user
        property_manager = Property_Manager.objects.get(user=request.user)
        
        # Fetch notifications related to this Property_Manager
        notifications = Notification.objects.filter(property_manager=property_manager).order_by('-created_at')
        
        # Extract maintenance requests from notifications
        maintenance_requests = [notification.maintenance_request for notification in notifications]
        
        # Serialize and return the data
        serializer = MaintenanceRequestSerializer(maintenance_requests, many=True)
        return Response(serializer.data)
    
    except Property_Manager.DoesNotExist:
        return Response({'detail': 'Property Manager not found'}, status=404)



# Endpoint to mark request as sent & trigger automated email to tenant
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_request_as_read(request, request_id):
    try:
        maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, property_manager__user=request.user)
        
        # Update the status of the request to "Request Read"
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

    except MaintenanceRequest.DoesNotExist:
        return Response({"error": "Maintenance request not found"}, status=status.HTTP_404_NOT_FOUND)



# To see & update status of maintenance request  
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_maintenance_request(request, request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, property_manager__user=request.user)
    
    if request.method == 'GET':
        serializer = MaintenanceRequestSerializer(maintenance_request)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data
        maintenance_request.priority = data.get('priority', maintenance_request.priority)
        maintenance_request.status = data.get('status', maintenance_request.status)
        maintenance_request.contractor_name = data.get('contractor_name', maintenance_request.contractor_name)
        maintenance_request.contractor_phone = data.get('contractor_phone', maintenance_request.contractor_phone)
        maintenance_request.property_manager_message = data.get('property_manager_message', maintenance_request.property_manager_message)

        # Save any additional images
        for image_file in request.FILES.getlist('additional_images'):
            image = Image(file=image_file, maintenance_request=maintenance_request)
            image.save()

        maintenance_request.save()
        
        # Generate the URL to the tenant's specific progress check page
        progress_check_url = request.build_absolute_uri(reverse('progress_check', kwargs={'request_number': maintenance_request.request_number}))

        # When the contractor's name and phone are provided, send an email to the tenant
        if maintenance_request.contractor_name and maintenance_request.contractor_phone:
            send_mail(
                subject="Appointment Set for Your Maintenance Request",
                message=f"Hello {maintenance_request.full_name},\n\nYour property manager has set an appointment with {maintenance_request.contractor_name} for your maintenance request. Please check your progress check page for more details. \n\nYou can track the progress of your request directly using the link below:\n\n{progress_check_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[maintenance_request.email],
                fail_silently=False,
            )

        return Response({"message": "Maintenance request updated successfully"}, status=status.HTTP_200_OK)


# If we want to protect certain views with JWT authentication, we will need to use the IsAuthenticated permission class in our views like this:

# class ExampleProtectedView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({'message': 'You have access to this view!'})
    
# Testing JWT Authentication
# We can test JWT authentication using Postman:
# Obtain Token: Make a POST request to /api/token/ with username & password to get the access & refresh tokens.
# Access Protected Endpoint: Use the access token in the Authorization header to access protected endpoints.