from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from authsystem.views import get_authenticated_user
from .models import SavedPlace


class IndexView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'online',
            'service': 'RideGo API',
            'version': '1.0.0',
            'message': 'Welcome to RideGo API',
            'endpoints': {
                'health': '/api/health/',
                'info': '/api/info/',
                'auth': {
                    'login': 'POST /api/auth/login/',
                    'verify': 'POST /api/auth/verify/',
                },
                'drivers': {
                    'register': 'POST /api/drivers/register/',
                    'toggle_online': 'POST /api/drivers/toggle-online/',
                    'update_location': 'POST /api/drivers/update-location/',
                    'nearby': 'GET /api/drivers/nearby/',
                    'documents': 'POST /api/drivers/documents/'
                },
                'rides': {
                    'request': 'POST /api/rides/request/',
                    'status': 'GET /api/rides/status/<id>/',
                    'accept': 'POST /api/rides/accept/',
                    'update_status': 'POST /api/rides/update-status/',
                    'cancel': 'POST /api/rides/cancel/'
                },
                'maps': {
                    'geocode': 'GET /api/maps/geocode/',
                    'reverse_geocode': 'GET /api/maps/reverse-geocode/',
                    'route': 'GET /api/maps/route/',
                    'autocomplete': 'GET /api/maps/autocomplete/'
                }
            }
        })


class SavedPlacesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        places = SavedPlace.objects.filter(user=user).order_by('-created_at')
        return Response({
            'success': True,
            'places': [
                {
                    'id': p.id,
                    'name': p.name,
                    'address': p.address,
                    'latitude': p.latitude,
                    'longitude': p.longitude,
                    'created_at': p.created_at.isoformat()
                }
                for p in places
            ]
        })

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        name = request.data.get('name')
        address = request.data.get('address')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not all([name, address, latitude, longitude]):
            return Response({
                'success': False,
                'message': 'name, address, latitude, longitude are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            place = SavedPlace.objects.create(
                user=user,
                name=name,
                address=address,
                latitude=float(latitude),
                longitude=float(longitude)
            )
            return Response({
                'success': True,
                'place': {
                    'id': place.id,
                    'name': place.name,
                    'address': place.address,
                    'latitude': place.latitude,
                    'longitude': place.longitude,
                    'created_at': place.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class SavedPlaceDetailView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, place_id):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            place = SavedPlace.objects.get(id=place_id, user=user)
            place.delete()
            return Response({
                'success': True,
                'message': 'Place deleted'
            })
        except SavedPlace.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Place not found'
            }, status=status.HTTP_404_NOT_FOUND)


class SupportContactView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'success': True,
            'contacts': [
                '+918273781021',
                '+919368605557'
            ]
        })


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})


class InfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'name': 'RideGo API',
            'description': 'Ride-hailing platform backend',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'login': 'POST /api/auth/login/',
                    'verify': 'POST /api/auth/verify/',
                },
                'drivers': {
                    'register': 'POST /api/drivers/register/',
                    'toggle_online': 'POST /api/drivers/toggle-online/',
                    'update_location': 'POST /api/drivers/update-location/',
                    'nearby': 'GET /api/drivers/nearby/',
                    'documents': 'POST /api/drivers/documents/'
                },
                'rides': {
                    'request': 'POST /api/rides/request/',
                    'status': 'GET /api/rides/status/<id>/',
                    'accept': 'POST /api/rides/accept/',
                    'update_status': 'POST /api/rides/update-status/',
                    'cancel': 'POST /api/rides/cancel/'
                },
                'maps': {
                    'geocode': 'GET /api/maps/geocode/',
                    'reverse_geocode': 'GET /api/maps/reverse-geocode/',
                    'route': 'GET /api/maps/route/',
                    'autocomplete': 'GET /api/maps/autocomplete/'
                }
            }
        })
