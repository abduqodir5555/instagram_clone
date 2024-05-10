from datetime import datetime

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, CodeVerify, REGESTIR, CODE_VERIFIED, NEW, PHOTO_STEP, DONE, RESET_PASSWORD
from users.serializers import SignUpSerializer, VerifyOtpSerializer, SendAgainCodeSerializer, regestir, forgot_password
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
