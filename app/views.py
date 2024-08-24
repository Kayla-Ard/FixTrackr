
from django.http import HttpResponse
from django.template import loader
from .models import Property_Manager, MaintenanceRequest, Image, Tenant
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
import logging
from django.contrib.auth import authenticate

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
                maintenance_request.save()

                # Process multiple image files
                for image_file in request.FILES.getlist('images'):
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












# PWA RESTful API endpoints

# Property manager register endpoint
@api_view(['POST'])
def register_property_manager(request):
    data = request.data

    # Validate password match
    if data.get('password') != data.get('confirm_password'):
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate email uniqueness
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Create user and property manager
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['firstName'],
            last_name=data['lastName']
        )

        property_manager = Property_Manager.objects.create(
            first_name=data['firstName'],
            last_name=data['lastName'],
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

        # Generate tokens
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
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# Property manager login endpoint
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, username=email, password=password)

    if user is not None:
        # Generate tokens
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
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)



# List properties
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_properties(request):
    properties = Property_Manager.objects.filter(user=request.user)
    serializer = PropertyManagerSerializer(properties, many=True)
    return Response(serializer.data)


# Create properties 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property(request):
    serializer = PropertyManagerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Properties
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_property(request, id):
    property = get_object_or_404(Property_Manager, id=id, user=request.user)
    serializer = PropertyManagerSerializer(property, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Properties
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request, id):
    property = get_object_or_404(Property_Manager, id=id, user=request.user)
    property.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# List maintenance request
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_maintenance_requests(request):
    requests = MaintenanceRequest.objects.filter(property_manager__user=request.user)
    serializer = MaintenanceRequestSerializer(requests, many=True)
    return Response(serializer.data)



# Update maintenance request
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_request_status(request, id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=id, property_manager__user=request.user)
    maintenance_request.status = request.data.get('status', maintenance_request.status)
    maintenance_request.save()
    return Response({'status': maintenance_request.status})







# If we want to protect certain views with JWT authentication, we will need to use the IsAuthenticated permission class in our views like this:

# class ExampleProtectedView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         return Response({'message': 'You have access to this view!'})
    
# Testing JWT Authentication
# We can test JWT authentication using Postman:
# Obtain Token: Make a POST request to /api/token/ with username & password to get the access & refresh tokens.
# Access Protected Endpoint: Use the access token in the Authorization header to access protected endpoints.