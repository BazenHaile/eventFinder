from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Event

def create_event_permissions():
    event_content_type = ContentType.objects.get_for_model(Event)
    Permission.objects.get_or_create(
        codename='can_manage_all_events',
        name='Can manage all events',
        content_type=event_content_type,
    )