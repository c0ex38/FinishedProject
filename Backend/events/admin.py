from django.contrib import admin
from .models import Event, EventParticipant, EventComment

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'organizer', 'event_type', 'start_date',
        'end_date', 'is_public', 'participant_count', 'is_past', 'is_ongoing'
    )
    list_filter = (
        'event_type', 'is_public', 'start_date',
        'end_date', 'created_at'
    )
    search_fields = (
        'title', 'description', 'organizer__username',
        'location__name'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Event Details', {
            'fields': (
                'title', 'description', 'organizer',
                'event_type', 'is_public', 'cover_image'
            )
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location & Participation', {
            'fields': (
                'location', 'online_link',
                'max_participants'
            )
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'event', 'status',
        'created_at', 'updated_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'user__username', 'event__title'
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'event', 'content_preview',
        'created_at'
    )
    list_filter = ('created_at',)
    search_fields = (
        'content', 'user__username',
        'event__title'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment Preview'
