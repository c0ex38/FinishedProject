from django.urls import path
from . import views

urlpatterns = [
    path('nearby/', views.nearby_locations, name='nearby-locations'),
    path('location/<int:location_id>/posts/', views.location_posts, name='location-posts'),
    path('discover/', views.discover_nearby_posts, name='discover-nearby-posts'),
]