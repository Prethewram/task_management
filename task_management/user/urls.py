from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from user.views import UserLoginView, UserRegistrationView, UserListView
from user import views

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-list'),
    #admin panel
    path('login/', views.login_view, name='login'),
    path('index/', views.index_view, name='index'),


]