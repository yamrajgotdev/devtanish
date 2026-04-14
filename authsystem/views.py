import random
import datetime
import secrets
from django.utils import timezone
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, OTP, AuthToken
from .serializers import UserSerializer, LoginSerializer, VerifyOTPSerializer


def get_bearer_token(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.replace('Bearer ', '', 1).strip()


def get_authenticated_user(request):
    token = get_bearer_token(request)
    if not token:
        return None
    try:
        auth_token = AuthToken.objects.select_related('user').get(key=token)
    except AuthToken.DoesNotExist:
        return None
    if auth_token.expires_at and timezone.now() > auth_token.expires_at:
        auth_token.delete()
        return None
    if not auth_token.user.is_active:
        return None
    return auth_token.user


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"DEBUG Login request data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG Login serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']

        # Create user if doesn't exist (signup), or get existing user (login)
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'is_active': True}
        )

        # Rate limiting: check for recent OTP requests
        cooldown_seconds = 60
        recent_otp = OTP.objects.filter(
            phone_number=phone_number,
            created_at__gte=timezone.now() - datetime.timedelta(seconds=cooldown_seconds)
        ).first()

        if recent_otp and not settings.DEV_BYPASS_OTP:
            return Response({
                'success': False,
                'message': f'Please wait {cooldown_seconds} seconds before requesting another OTP'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        if settings.DEV_BYPASS_OTP:
            otp_value = settings.DEV_OTP
        else:
            otp_value = str(random.randint(100000, 999999))

        expires_at = timezone.now() + datetime.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        OTP.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                'otp': otp_value,
                'is_verified': False,
                'attempts': 0,
                'expires_at': expires_at
            }
        )

        print(f"[DEV] OTP for {phone_number}: {otp_value}")

        if settings.DEV_BYPASS_OTP:
            return Response({
                'success': True,
                'message': 'OTP sent successfully',
                'new_user': created,
                'dev_mode': True,
                'otp': otp_value,
                'hint': 'Use OTP 123456 in dev mode'
            })

        # TODO: Integrate Twilio SMS API here
        # send_sms(phone_number, f"Your RideGo OTP is: {otp_value}")

        return Response({
            'success': True,
            'message': 'OTP sent successfully',
            'new_user': created
        })


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"DEBUG Verify request data: {request.data}")
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG Verify serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        otp_value = serializer.validated_data['otp']

        # Dev bypass: only works when DEBUG=True
        dev_bypass = settings.DEV_BYPASS_OTP and otp_value == settings.DEV_OTP

        if not dev_bypass:
            try:
                otp_record = OTP.objects.get(phone_number=phone_number)
            except OTP.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'OTP not found. Please request a new OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > otp_record.expires_at:
                return Response({
                    'success': False,
                    'message': 'OTP has expired. Please request a new OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.attempts >= 3:
                return Response({
                    'success': False,
                    'message': 'Too many attempts. Please request a new OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.otp != otp_value:
                otp_record.attempts += 1
                otp_record.save()
                return Response({
                    'success': False,
                    'message': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)

            otp_record.is_verified = True
            otp_record.save()

        # User already created in LoginView, just get it
        try:
            user = User.objects.get(phone_number=phone_number)
            is_new_user = False
        except User.DoesNotExist:
            # Fallback: create user if somehow not created
            user = User.objects.create(phone_number=phone_number, is_active=True)
            is_new_user = True

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        auth_token, _ = AuthToken.objects.update_or_create(
            user=user,
            defaults={
                'key': secrets.token_hex(32),
                'expires_at': None,
            },
        )

        user_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            'user': user_serializer.data,
            'new_user': is_new_user,
            'token': auth_token.key,
            'user_id': user.id,
        })


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'success': True,
            'phone_number': user.phone_number,
            'total_rides': user.total_rides,
            'member_since': user.created_at,
            'last_login': user.last_login,
            'is_active': user.is_active,
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Check authentication manually
        user = get_authenticated_user(request)
        if not user:
            return Response({
                'success': False,
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Delete the auth token to logout
        token = get_bearer_token(request)
        if token:
            try:
                auth_token = AuthToken.objects.get(key=token)
                auth_token.delete()
            except AuthToken.DoesNotExist:
                pass

        return Response({
            'success': True,
            'message': 'Logged out successfully'
        })
