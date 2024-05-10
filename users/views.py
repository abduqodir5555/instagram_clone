from datetime import datetime

from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, CodeVerify, REGESTIR, CODE_VERIFIED
from users.serializers import SignUpSerializer, VerifyOtpSerializer


class SignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class VerifyOtpView(APIView):
    http_method_names = ['post',]

    def post(self, request):
        data = request.data
        serializer = VerifyOtpSerializer(data = data)
        serializer.is_valid(raise_exception=True)
        id = data.get('id', None)
        code = data.get('code', None)

        try:
            user = User.objects.get(id=id)

        except User.DoestNotExist:
            data = {
                'status':False,
                'message':'Kiritilgan id ga tegishli user topilmadi'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            verify = CodeVerify.objects.get(user=user, code=code, verify_type=REGESTIR,
                                  expire_time__gte=datetime.now(), is_confirmed=False)

        except CodeVerify.DoesNotExist:
            data = {
                'status':False,
                'message':'code xato!!!'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        verify.is_confirmed = True
        verify.save()
        user.auth_status = CODE_VERIFIED
        user.save()
        data = {
            'status':True,
            'message':'otp code muvaffaqiyatli tasdiqlandi',
            'user_id':user.id,
            'auth_status':user.auth_status,
        }
        return Response(data, status=status.HTTP_200_OK)




