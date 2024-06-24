# Import necessary modules
from django.contrib import admin
from .models import Event, CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Custom admin class for the CustomUser model
class CustomUserAdmin(BaseUserAdmin):
    # Add custom fields to the default User admin fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('profile_picture', 'bio', 'contact_phone', 'saved_events')}),
    )
    
    # Add custom fields to the "add user" form in the admin
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('profile_picture', 'bio', 'contact_phone', 'saved_events')}),
    )

# Register the Event model with the default admin interface
admin.site.register(Event)

# Register the CustomUser model with the custom admin interface
admin.site.register(CustomUser, CustomUserAdmin)