from django.contrib import admin
from .models import (
    Group, GroupMember, GroupPost, GroupPostComment,
    GroupEvent, GroupEventParticipant, GroupChat, GroupChatMessage
)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'creator', 'created_at')
    list_filter = ('group_type', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'group', 'created_at')
    list_filter = ('created_at', 'group')
    search_fields = ('content', 'author__username', 'group__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupPostComment)
class GroupPostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupEvent)
class GroupEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'creator', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'created_at')
    search_fields = ('title', 'description', 'creator__username', 'group__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupEventParticipant)
class GroupEventParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('created_at',)

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('group', 'created_at')
    search_fields = ('group__name',)
    readonly_fields = ('created_at',)

@admin.register(GroupChatMessage)
class GroupChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'sender__username', 'chat__group__name')
    readonly_fields = ('created_at',)
