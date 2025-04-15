from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('users/', views.search_users, name='search-users'),
    path('posts/title/', views.search_posts_by_title, name='search-posts-by-title'),
    path('trending/', views.trending_hashtags, name='trending-hashtags'),
    path('hashtag/<str:hashtag_slug>/', views.hashtag_posts, name='hashtag-posts'),
]