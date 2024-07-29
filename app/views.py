
from django.http import HttpResponse
from django.template import loader
from .models import Property_Manager

def propertymanagers(request):
    property_managers = Property_Manager.objects.all().values()
    template = loader.get_template('property_manager.html')
    context = {
        'property_managers': property_managers,
    }
    return HttpResponse(template.render(context, request))


def details(request, id):
    property_managers = Property_Manager.objects.get(id=id)
    template = loader.get_template('details.html')
    context = {
        'property_managers': property_managers,
    }
    return HttpResponse(template.render(context, request))


def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())