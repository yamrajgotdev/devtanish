from django.contrib import admin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'vehicle_type', 'vehicle_number', 'is_approved', 'is_online', 'rating', 'total_rides']
    list_filter = ['is_approved', 'is_online', 'vehicle_type', 'created_at']
    search_fields = ['name', 'user__phone_number', 'vehicle_number', 'license_number', 'aadhaar_number']
    ordering = ['-created_at']
    readonly_fields = [
        'rating', 'total_rides', 'created_at', 'updated_at',
        'profile_photo', 'license_photo', 'rc_photo',
        'aadhaar_number', 'pan_number', 'license_number'
    ]

    fieldsets = (
        ('Driver Info', {
            'fields': ('user', 'name', 'phone_number')
        }),
        ('Documents & Verification', {
            'fields': (
                'profile_photo',
                'license_photo',
                'rc_photo',
                'license_number',
                'aadhaar_number',
                'pan_number',
            ),
            'description': 'Review uploaded documents before approving driver'
        }),
        ('Vehicle Info', {
            'fields': ('vehicle_type', 'vehicle_number')
        }),
        ('Approval & Status', {
            'fields': ('is_approved', 'is_online'),
            'description': 'Toggle approval status after reviewing documents'
        }),
        ('Location', {
            'fields': ('current_lat', 'current_lng', 'last_location_update'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('rating', 'total_rides', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def phone_number(self, obj):
        return obj.user.phone_number
    phone_number.short_description = 'Phone'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
