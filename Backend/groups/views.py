from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from .models import Group, GroupMember, GroupPost, GroupPostComment
from .serializers import (
    GroupSerializer, GroupMemberSerializer,
    GroupPostSerializer, GroupPostCommentSerializer
)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_list_create(request):
    if request.method == 'GET':
        groups = Group.objects.filter(group_type='public')
        serializer = GroupSerializer(groups, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Slug oluştur
            name = serializer.validated_data['name']
            slug = slugify(name)
            
            # Grubu oluştur
            group = serializer.save(
                creator=request.user,
                slug=slug
            )
            
            # Oluşturan kişiyi admin olarak ekle
            GroupMember.objects.create(
                group=group,
                user=request.user,
                role='admin',
                status='approved'
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    if request.method == 'GET':
        serializer = GroupSerializer(group, context={'request': request})
        return Response(serializer.data)
    
    # Yönetici yetkisi kontrolü
    membership = group.members.filter(user=request.user, status='approved').first()
    if not membership or membership.role not in ['admin', 'moderator']:
        return Response(
            {'error': 'Bu işlem için yetkiniz yok.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'PUT':
        serializer = GroupSerializer(group, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if membership.role != 'admin':
            return Response(
                {'error': 'Sadece grup yöneticisi grubu silebilir.'},
                status=status.HTTP_403_FORBIDDEN
            )
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    # Zaten üye mi kontrol et
    if GroupMember.objects.filter(group=group, user=request.user).exists():
        return Response(
            {'error': 'Zaten bu gruba üyesiniz veya üyelik isteğiniz var.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Grup tipine göre üyelik durumunu belirle
    status_type = 'approved' if group.group_type == 'public' else 'pending'
    
    member = GroupMember.objects.create(
        group=group,
        user=request.user,
        status=status_type
    )
    
    serializer = GroupMemberSerializer(member)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manage_member(request, slug, user_id):
    group = get_object_or_404(Group, slug=slug)
    member = get_object_or_404(GroupMember, group=group, user_id=user_id)
    
    # Yönetici yetkisi kontrolü
    admin_member = group.members.filter(
        user=request.user,
        status='approved',
        role__in=['admin', 'moderator']
    ).first()
    
    if not admin_member:
        return Response(
            {'error': 'Bu işlem için yetkiniz yok.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = GroupMemberSerializer(member, data=request.data, partial=True)
    if serializer.is_valid():
        # Moderatör, admin rolünü değiştiremez
        if admin_member.role == 'moderator' and 'role' in serializer.validated_data:
            return Response(
                {'error': 'Moderatörler rol değişikliği yapamaz.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Bu grubun gönderilerini görüntülemek için üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        posts = group.posts.all()
        serializer = GroupPostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GroupPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(group=group, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_post_comment(request, slug, post_id):
    group = get_object_or_404(Group, slug=slug)
    post = get_object_or_404(GroupPost, id=post_id, group=group)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Bu gönderiye yorum yapmak için gruba üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = GroupPostCommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_events(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Bu grubun etkinliklerini görüntülemek için üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        events = group.events.all()
        serializer = GroupEventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GroupEventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(group=group, creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_event_detail(request, slug, event_id):
    group = get_object_or_404(Group, slug=slug)
    event = get_object_or_404(GroupEvent, id=event_id, group=group)
    
    if request.method == 'GET':
        serializer = GroupEventSerializer(event, context={'request': request})
        return Response(serializer.data)
    
    # Etkinlik sahibi veya grup yöneticisi kontrolü
    if event.creator != request.user and not group.members.filter(
        user=request.user, status='approved', role__in=['admin', 'moderator']
    ).exists():
        return Response(
            {'error': 'Bu işlem için yetkiniz yok.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'PUT':
        serializer = GroupEventSerializer(event, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def group_event_participate(request, slug, event_id):
    group = get_object_or_404(Group, slug=slug)
    event = get_object_or_404(GroupEvent, id=event_id, group=group)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Etkinliğe katılmak için gruba üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    status_type = request.data.get('status', 'attending')
    
    participant, created = GroupEventParticipant.objects.get_or_create(
        event=event,
        user=request.user,
        defaults={'status': status_type}
    )
    
    if not created:
        participant.status = status_type
        participant.save()
    
    serializer = GroupEventParticipantSerializer(participant)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_chat(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Grup sohbetini görüntülemek için üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Sohbet yoksa oluştur
    chat, created = GroupChat.objects.get_or_create(group=group)
    
    # Son mesajları getir (örneğin son 50 mesaj)
    messages = chat.messages.all()[:50]
    serializer = GroupChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request, slug):
    group = get_object_or_404(Group, slug=slug)
    
    # Üyelik kontrolü
    if not group.members.filter(user=request.user, status='approved').exists():
        return Response(
            {'error': 'Mesaj göndermek için gruba üye olmalısınız.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    chat, created = GroupChat.objects.get_or_create(group=group)
    
    serializer = GroupChatMessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save(chat=chat, sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
