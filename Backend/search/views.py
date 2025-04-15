from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Hashtag
from .serializers import HashtagSerializer
from posts.models import Post
from posts.serializers import PostSerializer
from accounts.serializers import UserSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    """
    Genel arama: kullanıcılar, hashtag'ler ve içerik
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {'error': 'Arama sorgusu gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Hashtag araması
    if query.startswith('#'):
        tag_name = query[1:].lower()
        hashtags = Hashtag.objects.filter(name__icontains=tag_name)
        hashtag_serializer = HashtagSerializer(hashtags, many=True)
        return Response({'hashtags': hashtag_serializer.data})
    
    # Genel arama
    # Kullanıcı araması
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    )
    user_serializer = UserSerializer(users, many=True)
    
    # Hashtag araması
    hashtags = Hashtag.objects.filter(name__icontains=query)
    hashtag_serializer = HashtagSerializer(hashtags, many=True)
    
    # İçerik araması
    posts = Post.objects.filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) |
        Q(hashtags__hashtag__name__icontains=query)
    ).distinct()
    post_serializer = PostSerializer(posts, many=True, context={'request': request})
    
    return Response({
        'users': user_serializer.data,
        'hashtags': hashtag_serializer.data,
        'posts': post_serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """
    Sadece kullanıcı araması yapar
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {'error': 'Arama sorgusu gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    )
    
    # Sayfalama için limit ve offset parametrelerini al
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    
    # Sorguyu sınırla
    paginated_users = users[offset:offset+limit]
    
    serializer = UserSerializer(paginated_users, many=True)
    
    return Response({
        'count': users.count(),
        'next': offset + limit if offset + limit < users.count() else None,
        'previous': offset - limit if offset > 0 else None,
        'results': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_posts_by_title(request):
    """
    Post başlığına göre arama yapar
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {'error': 'Arama sorgusu gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    posts = Post.objects.filter(title__icontains=query, is_public=True)
    
    # Sayfalama için limit ve offset parametrelerini al
    limit = int(request.query_params.get('limit', 10))
    offset = int(request.query_params.get('offset', 0))
    
    # Sorguyu sınırla
    paginated_posts = posts[offset:offset+limit]
    
    serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
    
    return Response({
        'count': posts.count(),
        'next': offset + limit if offset + limit < posts.count() else None,
        'previous': offset - limit if offset > 0 else None,
        'results': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trending_hashtags(request):
    """
    Popüler hashtag'leri listeler
    """
    limit = int(request.query_params.get('limit', 10))
    hashtags = Hashtag.objects.all()[:limit]
    serializer = HashtagSerializer(hashtags, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hashtag_posts(request, hashtag_slug):
    """
    Belirli bir hashtag'e sahip gönderileri listeler
    """
    hashtag = Hashtag.objects.filter(slug=hashtag_slug).first()
    
    if not hashtag:
        return Response(
            {'error': 'Hashtag bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    posts = Post.objects.filter(hashtags__hashtag=hashtag, is_public=True)
    serializer = PostSerializer(posts, many=True, context={'request': request})
    
    return Response({
        'hashtag': HashtagSerializer(hashtag).data,
        'posts': serializer.data
    })
