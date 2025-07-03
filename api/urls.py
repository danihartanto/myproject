from django.urls import path
from .views import RegisterView, ProfileView, UpdateProfileView, CustomLoginView, LogoutView, ChangePasswordView, UserListView, UserDetailView, UserCRUDView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('sign_in/', CustomLoginView.as_view(), name='custom_token_obtain_pair'),
    path('auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout', LogoutView.as_view(), name='custom_logout'),
    path('auth/change-password', ChangePasswordView.as_view(), name='change_password'),
    path('user/profile', ProfileView.as_view(), name='profile'),
    path('user/profile/update', UpdateProfileView.as_view(), name='profile-update'),
    path('user/list', UserListView.as_view(), name='user-list'),
    path('user/<int:id>', UserDetailView.as_view(), name='user-detail'),
    
    path('users', UserCRUDView.as_view(), name='user-crud'),
    path('users/<int:id>', UserCRUDView.as_view(), name='user-crud-detail'),
    path('users/<int:id>/update/', UserCRUDView.as_view(), name='user-update'),
    
]
