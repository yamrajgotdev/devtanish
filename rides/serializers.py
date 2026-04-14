from rest_framework import serializers
from .models import Ride, RideRequest
from drivers.serializers import DriverSerializer


class RideSerializer(serializers.ModelSerializer):
    driver_details = DriverSerializer(source='driver', read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id', 'passenger', 'driver', 'driver_details',
            'pickup_lat', 'pickup_lng', 'pickup_address',
            'drop_lat', 'drop_lng', 'drop_address',
            'vehicle_type', 'status', 'distance_km',
            'estimated_fare', 'final_fare', 'otp',
            'requested_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'passenger', 'otp', 'requested_at', 'started_at', 'completed_at']


class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = ['id', 'ride', 'driver', 'distance_from_pickup', 'created_at', 'accepted']


class RideStatusSerializer(serializers.ModelSerializer):
    driver_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Ride
        fields = [
            'id', 'status', 'pickup_lat', 'pickup_lng', 'pickup_address',
            'drop_lat', 'drop_lng', 'drop_address', 'driver_details',
            'otp', 'distance_km', 'estimated_fare', 'final_fare'
        ]
    
    def get_driver_details(self, obj):
        if obj.driver:
            return {
                'id': obj.driver.id,
                'name': obj.driver.name,
                'phone_number': obj.driver.user.phone_number,
                'vehicle_type': obj.driver.vehicle_type,
                'vehicle_number': obj.driver.vehicle_number,
                'rating': obj.driver.rating,
                'current_lat': obj.driver.current_lat,
                'current_lng': obj.driver.current_lng
            }
        return None
