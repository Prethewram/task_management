from django.shortcuts import render 
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer, UserLoginSerializer

User = get_user_model()

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return User.objects.all()
        elif user.role == 'admin':
            return User.objects.filter(managed_by=user)
        return User.objects.filter(id=user.id)
    
#Admin panel

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse

def login_view(request):
    # Redirect already authenticated users
    if request.user.is_authenticated:
        if request.user.is_superadmin():
            return redirect(reverse('index'))
        else:
            return redirect(reverse('dashboard'))  # Assuming you have a dashboard for regular users
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Print for debugging
        print(f"Login attempt for user: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            
            # Redirect based on user type
            if hasattr(user, 'is_superadmin') and user.is_superadmin():
                return redirect(reverse('index'))
            else:
                return redirect(reverse('dashboard'))  # Change this to an appropriate URL for regular users
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def index_view(request):
    if not request.user.is_authenticated or not request.user.is_superadmin():
        return redirect(reverse('login'))
    return render(request, 'index.html')