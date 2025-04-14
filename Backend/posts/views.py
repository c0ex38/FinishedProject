from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Post, PostMedia, Like, Comment
from .serializers import PostSerializer, PostMediaSerializer, CommentSerializer
from django.db import transaction

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def post_list_create(request):
    """
    GET: Tüm gönderileri listeler
    POST: Yeni bir gönderi oluşturur
    """
    if request.method == 'GET':
        posts = Post.objects.filter(is_public=True)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Medya dosyası kontrolü
        if 'files' not in request.FILES:
            return Response(
                {'error': 'En az bir görsel veya video gereklidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Transaction ile post ve medya oluşturma
        with transaction.atomic():
            # Post verilerini hazırla
            post_data = {
                'title': request.data.get('title'),
                'content': request.data.get('content'),
                'latitude': request.data.get('latitude'),
                'longitude': request.data.get('longitude'),
                'location_name': request.data.get('location_name'),
                'is_public': request.data.get('is_public', True),
            }
            
            # Post oluştur
            serializer = PostSerializer(data=post_data, context={'request': request})
            if serializer.is_valid():
                post = serializer.save(author=request.user)
                
                # Birden fazla dosyayı işle
                files = request.FILES.getlist('files')
                
                # Dosya sayısı kontrolü
                if len(files) > 5:
                    post.delete()
                    return Response(
                        {'error': 'Bir gönderiye en fazla 5 medya eklenebilir.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Her dosyayı işle
                for index, file in enumerate(files):
                    file_name = file.name.lower()
                    
                    # Dosya tipini belirle
                    if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        media_type = 'image'
                    elif file_name.endswith(('.mp4', '.mov', '.avi')):
                        media_type = 'video'
                    else:
                        # Geçersiz dosya formatı, postu sil ve hata döndür
                        post.delete()
                        return Response(
                            {'error': f'Desteklenmeyen dosya formatı: {file_name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Medyayı kaydet
                    media = PostMedia(
                        post=post,
                        file=file,
                        media_type=media_type,
                        order=index  # Sıra numarası otomatik atanır
                    )
                    media.save()
                
                # Güncellenmiş post verilerini döndür
                serializer = PostSerializer(post, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, pk):
    """
    GET: Belirli bir gönderiyi görüntüler
    POST: Gönderiyi günceller
    DELETE: Gönderiyi siler
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Gizli gönderileri sadece yazarı görebilir
    if not post.is_public and post.author != request.user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)
    
    # Sadece yazar güncelleyebilir veya silebilir
    if post.author != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_post_media(request, pk):
    """
    Gönderiye medya (resim/video) ekler
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Sadece gönderi sahibi medya ekleyebilir
    if post.author != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # Mevcut medya sayısını kontrol et
    if post.media.count() >= 5:
        return Response(
            {'error': 'Bir gönderiye en fazla 5 medya eklenebilir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Medya tipini belirle
    file = request.data.get('file')
    if not file:
        return Response(
            {'error': 'Dosya gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Dosya uzantısına göre medya tipini belirle
    file_name = file.name.lower()
    if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        media_type = 'image'
    elif file_name.endswith(('.mp4', '.mov', '.avi')):
        media_type = 'video'
        
        # Video süresi kontrolü yapılabilir
        # from moviepy.editor import VideoFileClip
        # clip = VideoFileClip(file.temporary_file_path())
        # if clip.duration > 15:
        #     return Response(
        #         {'error': 'Video süresi en fazla 15 saniye olabilir.'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
    else:
        return Response(
            {'error': 'Desteklenmeyen dosya formatı.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Sıra numarasını belirle
    order = request.data.get('order', post.media.count())
    
    # Medyayı kaydet
    media = PostMedia(
        post=post,
        file=file,
        media_type=media_type,
        order=order
    )
    
    try:
        media.save()
        serializer = PostMediaSerializer(media)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_media_detail(request, pk, media_pk):
    """
    POST: Medya sırasını günceller
    DELETE: Medyayı siler
    """
    post = get_object_or_404(Post, pk=pk)
    media = get_object_or_404(PostMedia, pk=media_pk, post=post)
    
    # Sadece gönderi sahibi medyayı güncelleyebilir veya silebilir
    if post.author != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        # Sıra numarasını güncelle
        order = request.data.get('order')
        if order is not None:
            media.order = order
            media.save()
            return Response(PostMediaSerializer(media).data)
        return Response(
            {'error': 'Sıra numarası gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    elif request.method == 'DELETE':
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def like_post(request, pk):
    """
    POST: Gönderiyi beğenir
    DELETE: Gönderi beğenisini kaldırır
    """
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        # Daha önce beğenilmemişse beğeni ekle
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            # Beğeni sayısını güncelle
            post.likes_count = post.likes.count()
            post.save()
            return Response({'status': 'post liked'}, status=status.HTTP_201_CREATED)
        
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Beğeniyi kaldır
        like = Like.objects.filter(user=request.user, post=post)
        if like.exists():
            like.delete()
            # Beğeni sayısını güncelle
            post.likes_count = post.likes.count()
            post.save()
            return Response({'status': 'like removed'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'not liked'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_comments(request, pk):
    """
    GET: Gönderinin yorumlarını listeler
    POST: Gönderiye yeni yorum ekler
    """
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'GET':
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            
            # Yorum sayısını güncelle
            post.comments_count = post.comments.count()
            post.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, post_pk, comment_pk):
    """
    POST: Yorumu günceller
    DELETE: Yorumu siler
    """
    comment = get_object_or_404(Comment, pk=comment_pk, post__pk=post_pk)
    
    # Sadece yorum sahibi güncelleyebilir veya silebilir
    if comment.user != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        post = comment.post
        comment.delete()
        
        # Yorum sayısını güncelle
        post.comments_count = post.comments.count()
        post.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)