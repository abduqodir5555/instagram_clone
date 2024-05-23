from datetime import datetime

from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, CodeVerify, REGESTIR, CODE_VERIFIED, NEW, PHOTO_STEP, DONE, RESET_PASSWORD
from users.serializers import SignUpSerializer, VerifyOtpSerializer, SendAgainCodeSerializer, regestir, forgot_password, \
    UserInformationSerializer, PhotoStepSerializer, LoginSerializer
from users.utils import create_otp_code, send_code_email


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

        except:
            data = {
                'status': False,
                'message': 'Kiritilgan id ga tegishli user topilmadi'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            verify = CodeVerify.objects.get(user=user,
                                            code=code,
                                            verify_type=REGESTIR,
                                            expire_time__gte=datetime.now(),
                                            is_confirmed=False
                                            )

        except:
            data = {
                'status': False,
                'message': 'code xato!!!'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        verify.is_confirmed = True
        verify.save()
        user.auth_status = CODE_VERIFIED
        user.save()
        data = {
            'status': True,
            'message': 'otp code muvaffaqiyatli tasdiqlandi',
            'user_id': user.id,
            'auth_status': user.auth_status,
        }
        return Response(data, status=status.HTTP_200_OK)


class SendAgainCodeView(APIView):
    http_method_names = ['post', ]

    @staticmethod
    def check_active_otp_code(user):
        if CodeVerify.objects.filter(user=user, expire_time__gte=datetime.now()):
            data = {
                'status': False,
                'message': 'Sizning OTP codingiz hali yaroqli!!!'
            }
            print("worked")
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = request.data
        serializer = SendAgainCodeSerializer(data = data)
        serializer.is_valid(raise_exception=True)
        code_type = data.get('code_type', None)
        user_id = data.get('user_id', None)

        try:
            user = User.objects.get(id=user_id)
        except:
            data = {
                'status': False,
                'message': 'User topilmadi!!!'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if code_type == regestir:
            if user.auth_status != NEW:
                data = {
                    'status': False,
                    'message': 'Siz allaqachon ro\'yxatdan o\'tib bo\'lgansiz'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if CodeVerify.objects.filter(user=user, expire_time__gte=datetime.now(), verify_type=REGESTIR):
                data = {
                    'status': False,
                    'message': 'Sizning OTP codingiz hali yaroqli!!!'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # self.check_active_otp_code(user)
            code = create_otp_code()
            CodeVerify.objects.create(user=user,
                                      verify_type=REGESTIR,
                                      code=code
                                      )
            send_code_email(code, user.email)
            data = {
                'status': True,
                'message': 'Sizning OTP codingiz muvaffaqiyatli yuborildi!!!'
            }
            return Response(data, status=status.HTTP_200_OK)
        elif code_type == forgot_password:
            if not (user.auth_status in [PHOTO_STEP, DONE]):
                data = {
                    'status': False,
                    'message': "Siz hali ro'yxatdan o'tmagansiz!!!"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if CodeVerify.objects.filter(user=user, expire_time__gte=datetime.now(), verify_type=RESET_PASSWORD):
                data = {
                    'status': False,
                    'message': 'Sizning OTP codingiz hali yaroqli!!!'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            code = create_otp_code()
            CodeVerify.objects.create(user=user,
                                      verify_type=RESET_PASSWORD,
                                      code=code
                                      )
            send_code_email(code, user.email)
            data = {
                'status': True,
                'message': 'Sizning OTP codingiz muvaffaqiyatli yuborildi!!!'
            }
            return Response(data, status=status.HTTP_200_OK)


class UserInformationView(APIView):
    http_method_names = ['post', ]

    def post(self, request):
        try:
            user = User.objects.get(id=request.data.get('user_id', None))
        except:
            just = {
                'status': False,
                'message': 'User topilmadi!!!'
            }
            return Response(just, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInformationSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        print(data)
        

        serializer.save()

        just = {
            'status': True,
            'message': 'User has been updated successfully'
        }
        return Response(just, status=status.HTTP_200_OK)


class UserInformationView(generics.UpdateAPIView):
    http_method_names = ['post', 'put', 'patch']

    def get_object(self, request):
        user_id = request.data.get('user_id', None)
        try:
            user = User.objects.get(id=user_id)
            return user
        except:
            data = {
                'status': False,
                'message': 'User not found'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        user = self.get_object(request=request)
        serializer = UserInformationSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'status': True,
            'message': 'User information has been updated successfully',
            'user_id': user.id,
            'auth_status': user.auth_status,
            'is_active': user.is_active
        }
        return Response(data, status=status.HTTP_200_OK)


class PhotoStepView(APIView):
    http_method_names = ['post', ]
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id', None)
        user = User.objects.filter(id=user_id)
        if not user:
            data = {
                'status': False,
                'message': 'User not found'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        serializer = PhotoStepSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        image = data.get('photo', None)
        user = user[0]
        if user.auth_status != CODE_VERIFIED:
            data = {
                'status': False,
                'message': 'Siz ro\'yxatdan o\'tib bo\'lgansiz!!!'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if image:
            user.photo = image
            user.auth_status = DONE
            user.save()

        data = {
            'status': True,
            'message': 'Siz muvaffaqiyatli ro\'yxatdan o\'tdingiz',
            'auth_status': user.auth_status
        }
        return Response(data, status=status.HTTP_200_OK)


class LoginView(APIView):
    http_method_names = ['post', ]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_input = data.get('user_input', None)
        password = data.get('password', None)
        users = User.objects.filter(Q(username=user_input) | Q(email=user_input) | Q(phone_number=user_input))
        if not users:
            just = {
                'status': False,
                'message': 'User not found'
            }
            return Response(just, status=status.HTTP_400_BAD_REQUEST)
        user = users[0]
        username = user.username

        user = authenticate(username = username, password = password)

        if user is None:
            just = {
                'status': False,
                'message': 'Parol xato!!!'
            }
            return Response(just, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        data =  {
            "status": True,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }
        return Response(data, status=status.HTTP_200_OK)


class AccountView(APIView):
    http_method_names = ['get', ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        user = request.user
        data = {
            'status': True,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'bio': user.bio,
            'auth_status': user.auth_status,
            'auth_role': user.auth_role,
            'auth_type': user.auth_type,
        }
        return Response(data=data, status=status.HTTP_200_OK)







