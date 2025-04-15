from django.contrib import admin
from .models import UserRelationship

@admin.register(UserRelationship)
class UserRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'follower', 'followed',
        'created_at', 'get_duration'
    )
    
    list_filter = ('created_at',)
    
    search_fields = (
        'follower__username',
        'follower__email',
        'followed__username',
        'followed__email'
    )
    
    readonly_fields = ('created_at',)
    
    def get_duration(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(obj.created_at, timezone.now())
    get_duration.short_description = 'Following Duration'
