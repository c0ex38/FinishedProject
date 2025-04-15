from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserRelationship
from .serializers import UserRelationshipSerializer, UserBriefSerializer

User = get_user_model()

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """
    POST: Kullanıcıyı takip et
    DELETE: Kullanıcıyı takipten çık
    """
    # Kendini takip etmeyi engelle
    if int(user_id) == request.user.id:
        return Response(
            {'error': 'Kendinizi takip edemezsiniz.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Takip edilecek kullanıcıyı bul
    followed_user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        # Zaten takip ediliyor mu kontrol et
        relationship, created = UserRelationship.objects.get_or_create(
            follower=request.user,
            followed=followed_user
        )
        
        if created:
            serializer = UserRelationshipSerializer(relationship)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(
            {'status': 'already following'},
            status=status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        # Takipten çık
        relationship = UserRelationship.objects.filter(
            follower=request.user,
            followed=followed_user
        )
        
        if relationship.exists():
            relationship.delete()
            return Response(
                {'status': 'unfollowed'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'status': 'not following'},
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_followers(request, user_id=None):
    """
    Kullanıcının takipçilerini listeler
    """
    # Eğer user_id verilmemişse, mevcut kullanıcının takipçilerini getir
    target_user_id = user_id if user_id else request.user.id
    target_user = get_object_or_404(User, pk=target_user_id)
    
    # Takipçileri al
    followers = target_user.followers.all()
    follower_users = [rel.follower for rel in followers]
    
    serializer = UserBriefSerializer(follower_users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_following(request, user_id=None):
    """
    Kullanıcının takip ettiklerini listeler
    """
    # Eğer user_id verilmemişse, mevcut kullanıcının takip ettiklerini getir
    target_user_id = user_id if user_id else request.user.id
    target_user = get_object_or_404(User, pk=target_user_id)
    
    # Takip edilenleri al
    following = target_user.following.all()
    following_users = [rel.followed for rel in following]
    
    serializer = UserBriefSerializer(following_users, many=True)
    return Response(serializer.data)
