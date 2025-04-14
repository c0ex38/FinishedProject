from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register_user(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        password = request.data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.set_password(password)
        user.save()

        response_data = serializer.data
        response_data.pop('password', None)

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Kullanıcı girişi - username, email veya telefon numarası ile giriş yapabilir
    JWT token döndürür
    """
    login_field = request.data.get('login_field')
    password = request.data.get('password')
    
    if not login_field or not password:
        return Response(
            {'error': 'Lütfen giriş bilgisi ve şifre giriniz.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try to find the user
    user = None
    
    # Try with username directly
    from django.contrib.auth import authenticate
    user = authenticate(username=login_field, password=password)
    
    # Try with email
    if not user:
        try:
            user_obj = User.objects.get(email=login_field)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    # Try with phone number
    if not user:
        try:
            user_obj = User.objects.get(phone_number=login_field)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get user data
        serializer = UserSerializer(user)
        user_data = serializer.data
        
        # Update last seen and last login
        from django.utils import timezone
        user.is_online = True
        user.last_login = timezone.now()
        user.save()
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        }, status=status.HTTP_200_OK)
    
    return Response(
        {'error': 'Geçersiz giriş bilgileri.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Kullanıcı çıkışı - JWT token'ı blacklist'e ekler
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            # Token'ı blacklist'e ekle
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Kullanıcının online durumunu ve son görülme zamanını güncelle
            from django.utils import timezone
            user = request.user
            user.is_online = False
            user.last_seen = timezone.now()
            user.save()
            
            return Response({"success": "Başarıyla çıkış yapıldı."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Refresh token gerekli."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def user_profile(request):
    """
    GET: Kullanıcı profilini görüntüler
    POST: Kullanıcı profilini günceller
    """
    user = request.user
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Değiştirilmemesi gereken alanları request.data'dan çıkar
        mutable_data = request.data.copy()
        
        # id, username ve signup_method alanlarını çıkar
        if 'id' in mutable_data:
            mutable_data.pop('id')
        if 'username' in mutable_data:
            mutable_data.pop('username')
        if 'signup_method' in mutable_data:
            mutable_data.pop('signup_method')
        
        serializer = UserSerializer(user, data=mutable_data, partial=True)
        
        if serializer.is_valid():
            # Şifre değişikliği varsa ayrıca işle
            if 'password' in request.data:
                password = request.data.get('password')
                try:
                    validate_password(password)
                    user.set_password(password)
                except ValidationError as e:
                    return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
            # Diğer alanları güncelle
            serializer.save()
            
            # Şifre alanını yanıttan çıkar
            response_data = serializer.data
            response_data.pop('password', None)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Kullanıcı şifresini günceller
    """
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    # Gerekli alanların kontrolü
    if not current_password or not new_password:
        return Response(
            {'error': 'Mevcut şifre ve yeni şifre gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mevcut şifrenin doğruluğunu kontrol et
    if not user.check_password(current_password):
        return Response(
            {'error': 'Mevcut şifre yanlış.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Yeni şifreyi doğrula
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Şifreyi güncelle
    user.set_password(new_password)
    user.save()
    
    # Kullanıcıyı yeniden giriş yapmaya zorlamak için yeni token oluştur
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'success': 'Şifre başarıyla güncellendi.',
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }, status=status.HTTP_200_OK)