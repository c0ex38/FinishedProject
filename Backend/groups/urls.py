from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list_create, name='group-list-create'),
    path('<slug:slug>/', views.group_detail, name='group-detail'),
    path('<slug:slug>/join/', views.join_group, name='join-group'),
    path('<slug:slug>/members/<int:user_id>/', views.manage_member, name='manage-member'),
    path('<slug:slug>/posts/', views.group_posts, name='group-posts'),
    path('<slug:slug>/posts/<int:post_id>/comment/', views.group_post_comment, name='group-post-comment'),
    # Yeni eklenen etkinlik URL'leri
    path('<slug:slug>/events/', views.group_events, name='group-events'),
    path('<slug:slug>/events/<int:event_id>/', views.group_event_detail, name='group-event-detail'),
    path('<slug:slug>/events/<int:event_id>/participate/', views.group_event_participate, name='group-event-participate'),
    path('<slug:slug>/chat/', views.group_chat, name='group-chat'),
    path('<slug:slug>/chat/send/', views.send_chat_message, name='send-chat-message'),
]