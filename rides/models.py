from django.db import models
from authsystem.models import User
from drivers.models import Driver


class Ride(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('searching_driver', 'Searching Driver'),
        ('driver_assigned', 'Driver Assigned'),
        ('driver_arriving', 'Driver Arriving'),
        ('ride_started', 'Ride Started'),
        ('ride_completed', 'Ride Completed'),
        ('cancelled', 'Cancelled'),
    ]

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_rides')
    
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    pickup_address = models.CharField(max_length=500, blank=True)
    
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()
    drop_address = models.CharField(max_length=500, blank=True)
    
    vehicle_type = models.CharField(max_length=20, default='mini')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    distance_km = models.FloatField(null=True, blank=True)
    estimated_fare = models.FloatField(null=True, blank=True)
    final_fare = models.FloatField(null=True, blank=True)
    
    otp = models.CharField(max_length=6, blank=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    pickup_time = models.DateTimeField(null=True, blank=True)
    drop_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rides'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['passenger', 'status']),
            models.Index(fields=['driver', 'status']),
        ]

    def __str__(self):
        return f"Ride {self.id} - {self.status}"


class RideRequest(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='requests')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='ride_requests')
    distance_from_pickup = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ride_requests'
