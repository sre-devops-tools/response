from django.conf import settings
ZOOM_API_KEY = getattr(settings, 'ZOOM_API_KEY')
ZOOM_API_SECRET = getattr(settings, 'ZOOM_API_SECRET')
ZOOM_API_USER_ID = getattr(settings, 'ZOOM_API_USER_ID')