from django.urls import path
from .views import GeocodeView, ReverseGeocodeView, RouteView, AutocompleteView

urlpatterns = [
    path('geocode/', GeocodeView.as_view(), name='geocode'),
    path('reverse-geocode/', ReverseGeocodeView.as_view(), name='reverse_geocode'),
    path('route/', RouteView.as_view(), name='route'),
    path('autocomplete/', AutocompleteView.as_view(), name='autocomplete'),
]
