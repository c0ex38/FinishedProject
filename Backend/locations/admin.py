from django.contrib import admin
from .models import Location, PostLocation

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'city', 'country',
        'post_count', 'get_coordinates',
        'created_at'
    )
    list_filter = (
        'city', 'country', 'created_at'
    )
    search_fields = (
        'name', 'address', 'city',
        'country'
    )
    readonly_fields = ('post_count', 'created_at')
    
    def get_coordinates(self, obj):
        return f"({obj.latitude}, {obj.longitude})"
    get_coordinates.short_description = 'Coordinates'

    fieldsets = (
        ('Location Details', {
            'fields': (
                'name', 'address', 'city',
                'country'
            )
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Statistics', {
            'fields': ('post_count', 'created_at')
        }),
    )

@admin.register(PostLocation)
class PostLocationAdmin(admin.ModelAdmin):
    list_display = (
        'post', 'location', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = (
        'post__content', 'location__name',
        'location__city', 'location__country'
    )
    readonly_fields = ('created_at',)
