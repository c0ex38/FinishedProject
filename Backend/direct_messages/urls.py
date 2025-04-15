from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list_create, name='conversation-list-create'),
    path('<int:pk>/', views.conversation_detail, name='conversation-detail'),
    path('<int:pk>/messages/', views.send_message, name='send-message'),
]