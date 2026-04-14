from django.contrib import admin
from .models import Ride, RideRequest


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger_phone', 'driver_name', 'status', 'vehicle_type', 'distance_km', 'estimated_fare']
    list_filter = ['status', 'vehicle_type']
    search_fields = ['passenger__phone_number', 'driver__name', 'pickup_address', 'drop_address']
    ordering = ['-requested_at']
    readonly_fields = ['requested_at', 'started_at', 'completed_at']
    
    def passenger_phone(self, obj):
        return obj.passenger.phone_number
    passenger_phone.short_description = 'Passenger'
    
    def driver_name(self, obj):
        return obj.driver.name if obj.driver else '-'
    driver_name.short_description = 'Driver'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('passenger', 'driver')


@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'ride', 'driver', 'distance_from_pickup', 'accepted', 'created_at']
    list_filter = ['accepted']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('ride', 'driver')
