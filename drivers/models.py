from django.db import models
from authsystem.models import User


class Driver(models.Model):
    VEHICLE_TYPES = [
        ('mini', 'Mini'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('auto', 'Auto'),
        ('bike', 'Bike'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    name = models.CharField(max_length=100)
    
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='mini')
    vehicle_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    
    aadhaar_number = models.CharField(max_length=14, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    
    profile_photo = models.ImageField(upload_to='drivers/photos/', blank=True, null=True)
    license_photo = models.ImageField(upload_to='drivers/licenses/', blank=True, null=True)
    rc_photo = models.ImageField(upload_to='drivers/rc/', blank=True, null=True)
    
    is_approved = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    rating = models.FloatField(default=5.0)
    total_rides = models.IntegerField(default=0)
    
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'drivers'
        indexes = [
            models.Index(fields=['is_online', 'is_approved']),
            models.Index(fields=['vehicle_type']),
        ]

    def __str__(self):
        return f"{self.name} - {self.vehicle_type}"

    def can_go_online(self):
        return self.is_approved and all([
            self.license_number,
            self.vehicle_number,
            self.aadhaar_number
        ])
