from django.db import models
from django.conf import settings

class Group(models.Model):
    GROUP_TYPES = [
        ('public', 'Açık Grup'),
        ('private', 'Kapalı Grup'),
        ('secret', 'Gizli Grup'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    group_type = models.CharField(max_length=10, choices=GROUP_TYPES, default='public')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    cover_image = models.ImageField(upload_to='groups/covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class GroupMember(models.Model):
    MEMBER_ROLES = [
        ('member', 'Üye'),
        ('moderator', 'Moderatör'),
        ('admin', 'Yönetici'),
    ]
    
    MEMBER_STATUS = [
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('blocked', 'Engellendi'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    role = models.CharField(max_length=10, choices=MEMBER_ROLES, default='member')
    status = models.CharField(max_length=10, choices=MEMBER_STATUS, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'user')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_posts'
    )
    content = models.TextField()
    image = models.ImageField(upload_to='groups/posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} in {self.group.name}"

class GroupPostComment(models.Model):
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_post_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"


class GroupEvent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='events')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_group_events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    online_link = models.URLField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} - {self.group.name}"

class GroupEventParticipant(models.Model):
    event = models.ForeignKey(GroupEvent, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_event_participations')
    status = models.CharField(max_length=20, choices=[
        ('attending', 'Katılıyor'),
        ('maybe', 'Belki'),
        ('not_attending', 'Katılmıyor')
    ], default='attending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class GroupChat(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.group.name}"

class GroupChatMessage(models.Model):
    chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='group_chats/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat.group.name}"
