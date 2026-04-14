from django.urls import path
from .views import (
    DriverRegistrationView, DriverProfileView, ToggleOnlineView,
    UpdateLocationView, NearbyDriversView, DriverDocumentsView,
    DriverStatusView
)

urlpatterns = [
    path('register/', DriverRegistrationView.as_view(), name='driver_register'),
    path('profile/<str:phone_number>/', DriverProfileView.as_view(), name='driver_profile'),
    path('toggle-online/', ToggleOnlineView.as_view(), name='toggle_online'),
    path('update-location/', UpdateLocationView.as_view(), name='update_location'),
    path('nearby/', NearbyDriversView.as_view(), name='nearby_drivers'),
    path('documents/', DriverDocumentsView.as_view(), name='driver_documents'),
    path('status/', DriverStatusView.as_view(), name='driver_status'),
]
