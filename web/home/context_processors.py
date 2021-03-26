from django.conf import settings


def google_analytics_key(request):
    return {"GOOGLE_ANALYTICS_KEY": settings.GOOGLE_ANALYTICS_KEY}
