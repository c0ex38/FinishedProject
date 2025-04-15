from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'is_verified', 'is_private',
        'is_online', 'last_seen', 'date_joined', 'is_staff'
    )
    
    list_filter = (
        'is_verified', 'is_private', 'is_online',
        'gender', 'signup_method', 'is_staff',
        'is_superuser', 'is_active'
    )
    
    search_fields = (
        'username', 'email', 'first_name',
        'last_name', 'phone_number', 'location_name'
    )
    
    readonly_fields = ('last_seen', 'date_joined', 'last_login')
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'email',
                'bio', 'profile_picture', 'phone_number',
                'date_of_birth', 'gender', 'website'
            )
        }),
        ('Location', {
            'fields': (
                'latitude', 'longitude', 'location_name',
                'is_location_visible'
            )
        }),
        ('Status', {
            'fields': (
                'is_verified', 'is_private', 'is_online',
                'last_seen', 'signup_method'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'is_staff', 'is_superuser'
            ),
        }),
    )
    
    ordering = ('-date_joined',)
