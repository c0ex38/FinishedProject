from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Power, Sqrt
from .models import Location, PostLocation
from .serializers import LocationSerializer, PostLocationSerializer
from .utils import calculate_distance

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearby_locations(request):
    """
    Belirli bir konuma yakın lokasyonları listeler
    """
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')
    radius = float(request.query_params.get('radius', 10.0))  # km cinsinden yarıçap
    
    if not all([latitude, longitude]):
        return Response(
            {'error': 'Konum bilgisi gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    locations = Location.objects.all()
    
    # Her lokasyon için mesafe hesapla
    locations_with_distance = []
    for location in locations:
        distance = calculate_distance(
            latitude, longitude,
            location.latitude, location.longitude
        )
        if distance <= radius:
            location.distance = distance
            locations_with_distance.append(location)
    
    # Mesafeye göre sırala
    locations_with_distance.sort(key=lambda x: x.distance)
    
    serializer = LocationSerializer(locations_with_distance, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_posts(request, location_id):
    """
    Belirli bir lokasyondaki gönderileri listeler
    """
    location = Location.objects.get(pk=location_id)
    post_locations = PostLocation.objects.filter(location=location)
    serializer = PostLocationSerializer(post_locations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discover_nearby_posts(request):
    """
    Yakındaki gönderileri keşfet
    """
    latitude = request.query_params.get('latitude')
    longitude = request.query_params.get('longitude')
    radius = float(request.query_params.get('radius', 10.0))  # km cinsinden yarıçap
    limit = int(request.query_params.get('limit', 20))
    
    if not all([latitude, longitude]):
        return Response(
            {'error': 'Konum bilgisi gereklidir.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    post_locations = PostLocation.objects.all()
    
    # Her post için mesafe hesapla ve filtreleme yap
    posts_with_distance = []
    for post_location in post_locations:
        distance = calculate_distance(
            latitude, longitude,
            post_location.location.latitude, post_location.location.longitude
        )
        if distance <= radius:
            post_location.location.distance = distance
            posts_with_distance.append(post_location)
    
    # Mesafeye göre sırala ve limitle
    posts_with_distance.sort(key=lambda x: x.location.distance)
    posts_with_distance = posts_with_distance[:limit]
    
    serializer = PostLocationSerializer(posts_with_distance, many=True)
    return Response(serializer.data)
