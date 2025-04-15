from django.urls import path
from . import views

urlpatterns = [
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('followers/', views.user_followers, name='my-followers'),
    path('followers/<int:user_id>/', views.user_followers, name='user-followers'),
    path('following/', views.user_following, name='my-following'),
    path('following/<int:user_id>/', views.user_following, name='user-following'),
]