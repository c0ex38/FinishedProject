from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversation_list_create(request):
    """
    GET: Kullanıcının tüm konuşmalarını listeler
    POST: Yeni bir konuşma başlatır
    """
    if request.method == 'GET':
        # Kullanıcının katıldığı tüm konuşmaları getir
        conversations = request.user.conversations.all()
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Yeni konuşma başlat
        participant_id = request.data.get('participant_id')
        
        if not participant_id:
            return Response(
                {'error': 'Katılımcı ID\'si gereklidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kendisiyle konuşma başlatmayı engelle
        if int(participant_id) == request.user.id:
            return Response(
                {'error': 'Kendinizle konuşma başlatamazsınız.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Katılımcıyı bul
        participant = get_object_or_404(User, pk=participant_id)
        
        # Bu iki kullanıcı arasında zaten bir konuşma var mı kontrol et
        existing_conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=participant
        ).first()
        
        if existing_conversation:
            serializer = ConversationSerializer(existing_conversation, context={'request': request})
            return Response(serializer.data)
        
        # Yeni konuşma oluştur
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, participant)
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    """
    Belirli bir konuşmanın detaylarını ve mesajlarını getirir
    """
    # Konuşmanın varlığını ve kullanıcının bu konuşmaya katılımcı olduğunu kontrol et
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    # Konuşma detaylarını getir
    conversation_serializer = ConversationSerializer(conversation, context={'request': request})
    
    # Konuşmadaki mesajları getir
    messages = conversation.messages.all()
    message_serializer = MessageSerializer(messages, many=True)
    
    # Okunmamış mesajları okundu olarak işaretle
    unread_messages = messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True)
    
    return Response({
        'conversation': conversation_serializer.data,
        'messages': message_serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, pk):
    """
    Belirli bir konuşmaya yeni mesaj gönderir
    """
    # Konuşmanın varlığını ve kullanıcının bu konuşmaya katılımcı olduğunu kontrol et
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    content = request.data.get('content')
    if not content or not content.strip():
        return Response(
            {'error': 'Mesaj içeriği boş olamaz.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Yeni mesaj oluştur
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    # Konuşmanın son güncelleme zamanını güncelle
    conversation.save()  # updated_at alanı auto_now=True olduğu için otomatik güncellenir
    
    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
