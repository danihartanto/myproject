from django.urls import path
from .views import RegisterView, ProfileView, UpdateProfileView, CustomLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('sign_in/', CustomLoginView.as_view(), name='custom_token_obtain_pair'),
    path('sign_in/', CustomLoginView.as_view(), name='custom_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='profile-update'),
]
