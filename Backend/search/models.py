from django.db import models
from django.utils.text import slugify

class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    post_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-post_count']
    
    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class PostHashtag(models.Model):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='hashtags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'hashtag')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.post.id} - #{self.hashtag.name}"
