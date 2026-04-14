from django.urls import path
from .views import LoginView, VerifyOTPView, UserProfileView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyOTPView.as_view(), name='verify'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
