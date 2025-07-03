from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer, UserListSerializer, UserSerializer
from .serializers import UpdateUserSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from django.utils import timezone
from rest_framework.views import APIView

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .permissions import IsAdminUser, IsSuperUser, CustomAdminOrReadOnly

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
    permission_classes = [permissions.IsAuthenticated] # autentikasi untuk tiap request menggunakan token
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
    permission_classes = [IsAuthenticated] # autentikasi untuk tiap request menggunakan token
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        operation_description="Ganti password user",
        responses={
            200: openapi.Response('Password berhasil diganti'),
            400: openapi.Response('Request invalid / password lama salah')
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password berhasil diganti"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     tags=["2. User Management"],
    #     operation_description="Ambil semua data user.",
    #     responses={200: UserListSerializer(many=True)}
    # )
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response({"message": "Berhasil ambil data user", "data": serializer.data}, status=status.HTTP_200_OK)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
            serializer = UserListSerializer(user)
            return Response({
                "message": "Data user ditemukan",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                "message": "User tidak ditemukan"
            }, status=status.HTTP_404_NOT_FOUND)

class UserCRUDView(APIView):
    permission_classes = [IsAuthenticated] # autentikasi untuk tiap request menggunakan token
    #permission_classes = [IsSuperUser] # autentikasi untuk yang bisa update data user adalah hanya superadmin
    permission_classes = [CustomAdminOrReadOnly] # autentikasi untuk user lain hanya bisa read, tidak bisa create dan update.

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"message": "Berhasil ambil data user", "data": serializer.data}, status=status.HTTP_200_OK)
    
    def get(self, request, id=None):
        try:
            user = CustomUser.objects.get(id=id)
            serializer = UserListSerializer(user)
            return Response({
                "message": "Data user ditemukan",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                "message": "User tidak ditemukan"
            }, status=status.HTTP_404_NOT_FOUND)
            
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User berhasil ditambahkan",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Gagal menambahkan user",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data user berhasil diupdate",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "Gagal update user",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({
                "message": "User tidak ditemukan"
            }, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, id=None):
        try:
            user = CustomUser.objects.get(id=id)
            user.delete()
            return Response({"message": "User berhasil dihapus"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "User tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
