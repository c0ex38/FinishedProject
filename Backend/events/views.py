from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Event, EventParticipant, EventComment
from .serializers import (
    EventSerializer, EventParticipantSerializer,
    EventCommentSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_list_create(request):
    if request.method == 'GET':
        filter_type = request.query_params.get('filter', 'upcoming')
        events = Event.objects.filter(is_public=True)
        
        if filter_type == 'upcoming':
            events = events.filter(start_date__gt=timezone.now())
        elif filter_type == 'past':
            events = events.filter(end_date__lt=timezone.now())
        elif filter_type == 'ongoing':
            now = timezone.now()
            events = events.filter(start_date__lte=now, end_date__gte=now)
        elif filter_type == 'my':
            events = request.user.organized_events.all()
        
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'GET':
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)
    
    # Sadece organizatör düzenleyebilir/silebilir
    if event.organizer != request.user:
        return Response(
            {'error': 'Bu işlem için yetkiniz yok.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'PUT':
        serializer = EventSerializer(event, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def event_participate(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if event.is_past:
        return Response(
            {'error': 'Bu etkinlik sona erdi.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    participation, created = EventParticipant.objects.get_or_create(
        event=event,
        user=request.user,
        defaults={'status': 'pending'}
    )
    
    if not created:
        return Response(
            {'error': 'Zaten bu etkinliğe katılım isteği gönderdiniz.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = EventParticipantSerializer(participation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def event_comment(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    serializer = EventCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(event=event, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_participants(request, pk):
    event = get_object_or_404(Event, pk=pk)
    participants = event.participants.all()
    serializer = EventParticipantSerializer(participants, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_participant_status(request, event_pk, participant_pk):
    event = get_object_or_404(Event, pk=event_pk)
    
    if event.organizer != request.user:
        return Response(
            {'error': 'Bu işlem için yetkiniz yok.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    participant = get_object_or_404(EventParticipant, pk=participant_pk, event=event)
    
    serializer = EventParticipantSerializer(participant, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
