from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient', 'sender', 'notification_type',
        'text_preview', 'is_read', 'created_at'
    )
    
    list_filter = (
        'notification_type', 'is_read',
        'created_at'
    )
    
    search_fields = (
        'recipient__username', 'sender__username',
        'text', 'post__content'
    )
    
    readonly_fields = ('created_at',)
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Notification Text'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'recipient', 'sender',
                'notification_type', 'text'
            )
        }),
        ('Related Content', {
            'fields': ('post', 'comment', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
