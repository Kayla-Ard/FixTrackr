
def static_version(request):
    from django.conf import settings
    return {'STATIC_VERSION': settings.STATIC_VERSION}
