from django.db import models
from django.conf import settings

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    # Location information
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        help_text="Enlem (örnek: 37.123456)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        help_text="Boylam (örnek: 42.123456)"
    )
    location_name = models.CharField(
        max_length=255,
        blank=True, null=True,
        help_text="Şehir, semt ya da adres bilgisi"
    )
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username}'s post ({self.id})"
    
    @property
    def main_media(self):
        """Ana görseli veya videoyu döndürür"""
        media = self.media.all().order_by('order')
        return media.first() if media.exists() else None


class PostMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='posts/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Post Media'
        verbose_name_plural = 'Post Media'
        constraints = [
            models.UniqueConstraint(fields=['post', 'order'], name='unique_media_order')
        ]
    
    def __str__(self):
        return f"{self.post.id} - {self.media_type} ({self.order})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Hashtag'leri işle
        from search.utils import process_post_hashtags
        process_post_hashtags(self)
        
        # Lokasyon bilgisini işle
        if self.latitude and self.longitude:
            from locations.models import Location, PostLocation
            
            # Lokasyonu bul veya oluştur
            location, created = Location.objects.get_or_create(
                latitude=self.latitude,
                longitude=self.longitude,
                defaults={
                    'name': self.location_name or 'Unnamed Location',
                }
            )
            
            # Post ile lokasyonu ilişkilendir
            PostLocation.objects.get_or_create(post=self, location=location)
            
            # Lokasyon post sayısını güncelle
            location.post_count = location.posts.count()
            location.save()


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s comment on post {self.post.id}"
