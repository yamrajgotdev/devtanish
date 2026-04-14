from math import radians, cos, sin, sqrt, atan2
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

from .ola_maps import ola_maps


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km using haversine formula"""
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


class GeocodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        address = request.query_params.get('address')
        
        if not address:
            return Response({
                'success': False,
                'message': 'address parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        result = ola_maps.geocode(address)
        
        if result:
            return Response({
                'success': True,
                'result': result
            })
        
        return Response({
            'success': False,
            'message': 'Could not geocode address'
        }, status=status.HTTP_404_NOT_FOUND)


class ReverseGeocodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response({
                'success': False,
                'message': 'lat and lng parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            lng = float(lng)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid coordinates'
            }, status=status.HTTP_400_BAD_REQUEST)

        result = ola_maps.reverse_geocode(lat, lng)
        
        if result:
            return Response({
                'success': True,
                'result': result
            })
        
        return Response({
            'success': False,
            'message': 'Could not reverse geocode coordinates'
        }, status=status.HTTP_404_NOT_FOUND)


class RouteView(APIView):
    permission_classes = [AllowAny]

    def get_route_data(self, origin_lat, origin_lng, dest_lat, dest_lng, vehicle_type='mini'):
        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return None, {'success': False, 'message': 'origin_lat, origin_lng, dest_lat, dest_lng are required'}

        try:
            origin_lat = float(origin_lat)
            origin_lng = float(origin_lng)
            dest_lat = float(dest_lat)
            dest_lng = float(dest_lng)
        except ValueError:
            return None, {'success': False, 'message': 'Invalid coordinates'}

        result = ola_maps.get_route(origin_lat, origin_lng, dest_lat, dest_lng)
        print(f"DEBUG Ola result: {result}, coords: {origin_lat},{origin_lng} -> {dest_lat},{dest_lng}")

        if result:
            distance_km = result['distance_km']
            duration_minutes = result['duration_minutes']
        else:
            # Fallback: use haversine distance calculation
            distance_km = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
            duration_minutes = round(distance_km * 3)
            print(f"DEBUG Fallback haversine: {distance_km}km, {duration_minutes}min")

        # Calculate fare
        config = settings.FARE_CONFIG.get(vehicle_type, settings.FARE_CONFIG['mini'])
        estimated_fare = config['base_fare'] + (distance_km * config['per_km']) + (duration_minutes * config.get('per_minute', 0))

        return {
            'distance_km': round(distance_km, 2),
            'duration_minutes': round(duration_minutes, 0),
            'estimated_fare': round(estimated_fare, 2),
            'vehicle_type': vehicle_type
        }, None

    def get(self, request):
        origin_lat = request.query_params.get('origin_lat')
        origin_lng = request.query_params.get('origin_lng')
        dest_lat = request.query_params.get('dest_lat')
        dest_lng = request.query_params.get('dest_lng')
        vehicle_type = request.query_params.get('vehicle_type', 'mini')

        data, error = self.get_route_data(origin_lat, origin_lng, dest_lat, dest_lng, vehicle_type)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'distance_km': data['distance_km'],
            'duration_minutes': data['duration_minutes'],
            'estimated_fare': data['estimated_fare']
        })

    def post(self, request):
        # Support both query params and body
        origin_lat = request.data.get('origin_lat') or request.query_params.get('origin_lat')
        origin_lng = request.data.get('origin_lng') or request.query_params.get('origin_lng')
        dest_lat = request.data.get('dest_lat') or request.query_params.get('dest_lat')
        dest_lng = request.data.get('dest_lng') or request.query_params.get('dest_lng')
        vehicle_type = request.data.get('vehicle_type') or request.query_params.get('vehicle_type', 'mini')

        data, error = self.get_route_data(origin_lat, origin_lng, dest_lat, dest_lng, vehicle_type)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'distance_km': data['distance_km'],
            'duration_minutes': data['duration_minutes'],
            'estimated_fare': data['estimated_fare']
        })


class AutocompleteView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        input_text = request.query_params.get('input')
        
        if not input_text:
            return Response({
                'success': False,
                'message': 'input parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        predictions = ola_maps.autocomplete(input_text)
        
        return Response({
            'success': True,
            'predictions': predictions
        })
