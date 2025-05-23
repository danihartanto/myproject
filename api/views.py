from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer
from .serializers import UpdateUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth import get_user_model

User = get_user_model()

# class CustomLoginView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         # Panggil TokenObtainPairView untuk generate token dan validasi login
#         response = super().post(request, *args, **kwargs)

#         # Cek apakah login berhasil dengan validasi token
#         if 'access' in response.data:
#             user = request.user
#             if user.is_authenticated:
#                 # Update last_login setelah login berhasil
#                 user.last_login = timezone.now()
#                 user.save()

#                 # Tambahkan message dan data user
#                 response.data['message'] = 'Login berhasil cak.'
#                 response.data['user'] = {
#                     'id': user.id,
#                     'email': user.email,
#                     'name': user.name,
#                     'last_login' : timezone.now(),
#                 }
#         else:
#             # Jika tidak ada token yang berhasil, beri pesan error
#             return Response({
#                 "message": "Login gagal, silakan coba lagi."
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         return response

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({
                "message": "Email atau password salah.",
                "detail": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = CustomUser.objects.get(email=request.data.get('email'))

        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "message": "User berhasil didaftarkan.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({
            "message": "Berhasil mengambil data profil.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Profil berhasil diperbarui.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Logout berhasil.",
                "code": 200
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "Logout gagal.",
                "code": 400,
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        # Validasi old_password
        if not user.check_password(old_password):
            return Response({
                "message": "Password lama salah.",
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validasi new_password tidak kosong
        if not new_password:
            return Response({
                "message": "Password baru tidak boleh kosong.",
                "code": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ganti password
        user.set_password(new_password)
        user.save()

        return Response({
            "message": "Password berhasil diubah.",
            "code": 200
        }, status=status.HTTP_200_OK)