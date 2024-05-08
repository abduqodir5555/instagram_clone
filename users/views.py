from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from users.models import User, CodeVerify
from users.serializers import SignUpSerializer


class SignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
