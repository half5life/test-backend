from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import UserRegistrationSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        # Мягкое удаление: деактивируем пользователя
        instance.is_active = False
        instance.save()

        # Добавляем все активные токены пользователя в черный список
        tokens = OutstandingToken.objects.filter(user=instance)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
