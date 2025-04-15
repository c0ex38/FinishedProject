from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list_create, name='event-list-create'),
    path('<int:pk>/', views.event_detail, name='event-detail'),
    path('<int:pk>/participate/', views.event_participate, name='event-participate'),
    path('<int:pk>/comment/', views.event_comment, name='event-comment'),
    path('<int:pk>/participants/', views.event_participants, name='event-participants'),
    path('<int:event_pk>/participants/<int:participant_pk>/status/',
         views.update_participant_status, name='update-participant-status'),
]