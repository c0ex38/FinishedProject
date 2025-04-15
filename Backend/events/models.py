from django.db import models
from django.conf import settings
from django.utils import timezone

class Event(models.Model):
    EVENT_TYPES = [
        ('online', 'Online Etkinlik'),
        ('offline', 'Yüz Yüze Etkinlik'),
        ('hybrid', 'Karma Etkinlik'),
    ]
    
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    online_link = models.URLField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='events/covers/', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return self.end_date < timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def participant_count(self):
        return self.participants.count()

class EventParticipant(models.Model):
    PARTICIPATION_STATUS = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('declined', 'Reddedildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_participations'
    )
    status = models.CharField(max_length=10, choices=PARTICIPATION_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('event', 'user')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title}"
