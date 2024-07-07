from django.urls import path
from .views import login_user, create_group, create_user
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/auth/login_user', login_user, name='login_user'),
    path('api/auth/create_user', create_user, name='create_user'),
    path('api/auth/create_group', create_group, name='create_group'),
    path('api/auth/refresh_token', TokenRefreshView.as_view(), name='refresh_token')
]