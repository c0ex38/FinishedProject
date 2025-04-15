from django.contrib import admin
from .models import Hashtag, PostHashtag

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'post_count',
        'created_at'
    )
    
    list_filter = ('created_at',)
    
    search_fields = ('name', 'slug')
    
    readonly_fields = (
        'slug', 'post_count',
        'created_at'
    )
    
    ordering = ('-post_count',)

@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    list_display = (
        'hashtag', 'post', 'created_at'
    )
    
    list_filter = ('created_at', 'hashtag')
    
    search_fields = (
        'hashtag__name',
        'post__content',
        'post__author__username'
    )
    
    readonly_fields = ('created_at',)
