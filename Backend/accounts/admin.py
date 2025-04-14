from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Add custom fields to list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'is_private', 'is_online')
    
    # Add filters
    list_filter = ('is_verified', 'is_private', 'is_online', 'gender', 'signup_method')
    
    # Add search fields
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'location_name')
    
    # Organize fields in fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture', 
                                     'phone_number', 'date_of_birth', 'gender', 'website')}),
        ('Location', {'fields': ('latitude', 'longitude', 'location_name', 'is_location_visible')}),
        ('Account settings', {'fields': ('is_verified', 'is_private', 'signup_method')}),
        ('Status', {'fields': ('is_online', 'last_seen')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

# Register the model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
