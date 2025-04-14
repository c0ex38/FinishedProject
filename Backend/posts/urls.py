from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_create, name='post-list-create'),
    path('<int:pk>/', views.post_detail, name='post-detail'),
    path('<int:pk>/media/', views.add_post_media, name='add-post-media'),
    path('<int:pk>/media/<int:media_pk>/', views.post_media_detail, name='post-media-detail'),
    path('<int:pk>/like/', views.like_post, name='post-like'),
    path('<int:pk>/comments/', views.post_comments, name='post-comments'),
    path('<int:post_pk>/comments/<int:comment_pk>/', views.comment_detail, name='comment-detail'),
    path('<int:post_pk>/comments/<int:comment_pk>/replies/', views.comment_replies, name='comment-replies'),
]