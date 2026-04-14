import random
from math import radians, cos, sin, sqrt, atan2
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Ride, RideRequest
from .serializers import RideSerializer, RideStatusSerializer
from drivers.models import Driver
from authsystem.views import get_authenticated_user


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calculate_fare(distance_km, vehicle_type, duration_minutes=0):
    config = settings.FARE_CONFIG.get(vehicle_type, settings.FARE_CONFIG['mini'])
    return config['base_fare'] + (distance_km * config['per_km']) + (duration_minutes * config.get('per_minute', 0))


class RequestRideView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        pickup_lat = request.data.get('pickup_lat')
        pickup_lng = request.data.get('pickup_lng')
        drop_lat = request.data.get('drop_lat')
        drop_lng = request.data.get('drop_lng')
        pickup_address = request.data.get('pickup_address', '')
        drop_address = request.data.get('drop_address', '')
        vehicle_type = request.data.get('vehicle_type', 'mini')

        if not all([pickup_lat, pickup_lng, drop_lat, drop_lng]):
            return Response({
                'success': False,
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        pickup_lat = float(pickup_lat)
        pickup_lng = float(pickup_lng)
        drop_lat = float(drop_lat)
        drop_lng = float(drop_lng)

        distance_km = haversine_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
        estimated_fare = calculate_fare(distance_km, vehicle_type)
        otp = str(random.randint(100000, 999999))

        ride = Ride.objects.create(
            passenger=user,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            pickup_address=pickup_address,
            drop_lat=drop_lat,
            drop_lng=drop_lng,
            drop_address=drop_address,
            vehicle_type=vehicle_type,
            distance_km=round(distance_km, 2),
            estimated_fare=round(estimated_fare, 2),
            otp=otp,
            status='searching_driver'
        )

        nearby_drivers = Driver.objects.filter(
            is_online=True,
            is_approved=True,
            vehicle_type=vehicle_type
        ).exclude(assigned_rides__status__in=['driver_assigned', 'driver_arriving', 'ride_started'])

        driver_list = []
        for driver in nearby_drivers:
            if driver.current_lat and driver.current_lng:
                dist = haversine_distance(
                    pickup_lat, pickup_lng,
                    driver.current_lat, driver.current_lng
                )
                if dist <= settings.DRIVER_SEARCH_RADIUS_KM:
                    driver_list.append({
                        'id': driver.id,
                        'name': driver.name,
                        'distance_km': round(dist, 2)
                    })

        driver_list.sort(key=lambda x: x['distance_km'])

        return Response({
            'success': True,
            'message': 'Ride requested successfully',
            'ride': {
                'id': ride.id,
                'status': ride.status,
                'pickup_lat': ride.pickup_lat,
                'pickup_lng': ride.pickup_lng,
                'drop_lat': ride.drop_lat,
                'drop_lng': ride.drop_lng,
                'distance_km': ride.distance_km,
                'estimated_fare': ride.estimated_fare,
                'otp': otp
            },
            'nearby_drivers': driver_list[:5]
        }, status=status.HTTP_201_CREATED)


class RideStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
            serializer = RideStatusSerializer(ride)
            return Response({
                'success': True,
                'ride': serializer.data
            })
        except Ride.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ride not found'
            }, status=status.HTTP_404_NOT_FOUND)


class AcceptRideView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        ride_id = request.data.get('ride_id')

        if not ride_id:
            return Response({
                'success': False,
                'message': 'ride_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Driver not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if not driver.is_online:
            return Response({
                'success': False,
                'message': 'Driver is not online'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not driver.is_approved:
            return Response({
                'success': False,
                'message': 'Driver is not approved'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            with transaction.atomic():
                # Lock the ride row to prevent race conditions
                ride = Ride.objects.select_for_update().get(id=ride_id)

                if ride.status not in ['searching_driver']:
                    return Response({
                        'success': False,
                        'message': 'Ride is not available for acceptance'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if ride.driver:
                    return Response({
                        'success': False,
                        'message': 'Ride already has a driver assigned'
                    }, status=status.HTTP_400_BAD_REQUEST)

                ride.driver = driver
                ride.status = 'driver_assigned'
                ride.save()
        except Ride.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ride not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'message': 'Ride accepted successfully',
            'ride': {
                'id': ride.id,
                'status': ride.status,
                'otp': ride.otp,
                'pickup_address': ride.pickup_address,
                'drop_address': ride.drop_address,
                'pickup_lat': ride.pickup_lat,
                'pickup_lng': ride.pickup_lng
            }
        })


class UpdateRideStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        ride_id = request.data.get('ride_id')
        new_status = request.data.get('status')

        if not all([ride_id, new_status]):
            return Response({
                'success': False,
                'message': 'ride_id and status are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = ['driver_arriving', 'ride_started', 'ride_completed', 'cancelled']
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver = Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Driver not found'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            ride = Ride.objects.get(id=ride_id, driver=driver)
        except Ride.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ride not found or not assigned to this driver'
            }, status=status.HTTP_404_NOT_FOUND)

        ride.status = new_status
        
        if new_status == 'ride_started':
            ride.started_at = timezone.now()
        elif new_status == 'ride_completed':
            ride.completed_at = timezone.now()
            ride.final_fare = ride.estimated_fare
            driver.total_rides += 1
            driver.is_online = True
            driver.save()
            ride.passenger.total_rides += 1
            ride.passenger.save(update_fields=['total_rides'])
        
        ride.save()

        return Response({
            'success': True,
            'message': f'Ride status updated to {new_status}',
            'ride': {
                'id': ride.id,
                'status': ride.status,
                'final_fare': ride.final_fare
            }
        })


class CancelRideView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        ride_id = request.data.get('ride_id')

        if not ride_id:
            return Response({
                'success': False,
                'message': 'ride_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ride = Ride.objects.get(id=ride_id, passenger=user)
        except Ride.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ride not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if ride.status in ['ride_started', 'ride_completed']:
            return Response({
                'success': False,
                'message': 'Cannot cancel ride that has already started'
            }, status=status.HTTP_400_BAD_REQUEST)

        ride.status = 'cancelled'
        ride.save()

        if ride.driver:
            ride.driver.is_online = True
            ride.driver.save()

        return Response({
            'success': True,
            'message': 'Ride cancelled successfully'
        })


class PassengerRidesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        rides = Ride.objects.filter(passenger=user).order_by('-requested_at')[:20]
        serializer = RideSerializer(rides, many=True)

        return Response({
            'success': True,
            'rides': serializer.data
        })


class UserRideHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        rides = Ride.objects.filter(passenger=user).select_related('driver').order_by('-requested_at')
        ride_list = []
        for ride in rides:
            driver_name = ride.driver.name if ride.driver else 'Not assigned'
            ride_list.append({
                'ride_id': ride.id,
                'pickup': ride.pickup_address or f"{ride.pickup_lat}, {ride.pickup_lng}",
                'destination': ride.drop_address or f"{ride.drop_lat}, {ride.drop_lng}",
                'fare': ride.final_fare if ride.final_fare is not None else ride.estimated_fare,
                'driver_name': driver_name,
                'date': ride.requested_at,
                'ride_status': ride.status,
            })

        return Response({
            'success': True,
            'total_rides': rides.count(),
            'rides': ride_list,
        })


class DriverRidesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        try:
            driver = Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Driver not found'
            }, status=status.HTTP_404_NOT_FOUND)

        rides = Ride.objects.filter(driver=driver).order_by('-requested_at')[:20]
        serializer = RideSerializer(rides, many=True)

        return Response({
            'success': True,
            'rides': serializer.data
        })


class FeedbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        ride_id = request.data.get('ride_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if not ride_id or not rating:
            return Response({
                'success': False,
                'message': 'ride_id and rating are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ride = Ride.objects.get(id=ride_id, passenger=user)
        except Ride.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ride not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if ride.status != 'ride_completed':
            return Response({
                'success': False,
                'message': 'Feedback can only be provided for completed rides'
            }, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Store feedback in database when Feedback model is created
        # For now, just return success

        return Response({
            'success': True,
            'message': 'Feedback submitted successfully'
        })


class DriverRideHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            driver = Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Driver not found'
            }, status=status.HTTP_404_NOT_FOUND)

        rides = Ride.objects.filter(driver=driver).order_by('-requested_at')
        serializer = RideSerializer(rides, many=True)

        return Response({
            'success': True,
            'rides': serializer.data
        })
