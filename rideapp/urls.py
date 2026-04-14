from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from authsystem.views import UserProfileView
from rides.views import UserRideHistoryView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/', include('authsystem.urls')),
    path('api/drivers/', include('drivers.urls')),
    path('api/rides/', include('rides.urls')),
    path('api/maps/', include('utils.urls')),
    path('api/user/profile', UserProfileView.as_view(), name='user_profile'),
    path('api/user/rides', UserRideHistoryView.as_view(), name='user_ride_history'),
]
