
from django.http import HttpResponse
from django.template import loader
from .models import Property_Manager, MaintenanceRequest, Image
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from .forms import MaintenanceRequestForm
import uuid
from .serializers import MaintenanceRequestSerializer, PropertyManagerSerializer
from rest_framework.views import APIView

# Tenant related HTML Views

def tenant_home(request):
    return render(request, 'tenant_home.html')


def generate_request_number():
    return str(uuid.uuid4()).split('-')[0].upper()


def submit_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.request_number = generate_request_number()
            maintenance_request.save()

            # Process each image field separately
            image_fields = ['image1', 'image2', 'image3', 'image4']
            for image_field in image_fields:
                image_file = request.FILES.get(image_field)
                if image_file:
                    image = Image(file=image_file)
                    image.save()
                    setattr(maintenance_request, image_field, image)

            maintenance_request.save()
            return render(request, 'request_submitted.html', {'request_number': maintenance_request.request_number})
        else:
            print(form.errors)  # Output errors for inspection
            return render(request, 'submit_request.html', {'form': form})
    else:
        form = MaintenanceRequestForm()
    return render(request, 'submit_request.html', {'form': form})


def check_request_status(request):
    if request.method == 'POST':
        request_number = request.POST.get('request_number')
        maintenance_request = get_object_or_404(MaintenanceRequest, request_number=request_number)
        return render(request, 'request_status.html', {'maintenance_request': maintenance_request})
    return render(request, 'check_request_status.html')


def progress_check(request):
    if request.method == 'POST':
        request_number = request.POST.get('request_number')
        maintenance_request = get_object_or_404(MaintenanceRequest, request_number=request_number)
        return render(request, 'progress_check.html', {'maintenance_request': maintenance_request})
    return render(request, 'progress_check.html')




# Mobile App/ RESTful API endpoint

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_request_api(request):
    serializer = MaintenanceRequestSerializer(data=request.data)
    if serializer.is_valid():
        maintenance_request = serializer.save()
        maintenance_request.request_number = generate_request_number()
        maintenance_request.save()

        # Handle file uploads if included in the request
        files = request.FILES.getlist('images')
        for file in files:
            image = Image(file=file, maintenance_request=maintenance_request)
            image.save()

        return Response({'request_number': maintenance_request.request_number}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check_status_api(request):
    request_number = request.query_params.get('request_number', None)
    if request_number:
        try:
            maintenance_request = MaintenanceRequest.objects.get(request_number=request_number)
            serializer = MaintenanceRequestSerializer(maintenance_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MaintenanceRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Request number is required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_requests(request):
    requests = MaintenanceRequest.objects.all()
    serializer = MaintenanceRequestSerializer(requests, many=True)
    return Response(serializer.data)



# Property manager API endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def property_managers_api(request):
    property_managers = Property_Manager.objects.all()
    serializer = PropertyManagerSerializer(property_managers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def property_manager_details_api(request, id):
    property_manager = get_object_or_404(Property_Manager, id=id)
    serializer = PropertyManagerSerializer(property_manager)
    return Response(serializer.data)





# If we want to protect certain views with JWT authentication, we will need to use the IsAuthenticated permission class in our views like this:

class ExampleProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'You have access to this view!'})
    
# Testing JWT Authentication
# We can test JWT authentication using Postman:
# Obtain Token: Make a POST request to /api/token/ with username & password to get the access & refresh tokens.
# Access Protected Endpoint: Use the access token in the Authorization header to access protected endpoints.