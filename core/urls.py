from django.urls import path
from .views import IndexView, HealthView, InfoView, SavedPlacesView, SavedPlaceDetailView, SupportContactView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('health/', HealthView.as_view(), name='health'),
    path('info/', InfoView.as_view(), name='info'),
    path('saved-places/', SavedPlacesView.as_view(), name='saved_places'),
    path('saved-places/<int:place_id>/', SavedPlaceDetailView.as_view(), name='saved_place_detail'),
    path('support/contact/', SupportContactView.as_view(), name='support_contact'),
]
