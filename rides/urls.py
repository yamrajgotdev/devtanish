from django.urls import path
from .views import (
    RequestRideView, RideStatusView, AcceptRideView,
    UpdateRideStatusView, CancelRideView,
    PassengerRidesView, DriverRidesView, FeedbackView,
    DriverRideHistoryView
)

urlpatterns = [
    path('request/', RequestRideView.as_view(), name='request_ride'),
    path('status/<int:ride_id>/', RideStatusView.as_view(), name='ride_status'),
    path('accept/', AcceptRideView.as_view(), name='accept_ride'),
    path('update-status/', UpdateRideStatusView.as_view(), name='update_ride_status'),
    path('cancel/', CancelRideView.as_view(), name='cancel_ride'),
    path('passenger/', PassengerRidesView.as_view(), name='passenger_rides'),
    path('driver/', DriverRidesView.as_view(), name='driver_rides'),
    path('driver-history/', DriverRideHistoryView.as_view(), name='driver_history'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]
