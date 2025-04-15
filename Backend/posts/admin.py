from django.contrib import admin
from .models import Post, PostMedia, Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'title', 'content_preview',
        'is_public', 'likes_count', 'comments_count',
        'shares_count', 'created_at'
    )
    
    list_filter = (
        'is_public', 'created_at',
        'author__is_staff'
    )
    
    search_fields = (
        'title', 'content', 'author__username',
        'location_name'
    )
    
    readonly_fields = (
        'created_at', 'updated_at',
        'likes_count', 'comments_count', 'shares_count'
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = (
        'post', 'media_type', 'order',
        'file', 'created_at'
    )
    list_filter = ('media_type', 'created_at')
    search_fields = ('post__content', 'post__author__username')
    readonly_fields = ('created_at',)
    ordering = ('post', 'order')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'user__username', 'post__content',
        'post__author__username'
    )
    readonly_fields = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'post', 'content_preview',
        'parent', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = (
        'content', 'user__username',
        'post__content', 'post__author__username'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'
