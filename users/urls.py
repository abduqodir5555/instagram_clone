from django.urls import path
from users.views import SignUpView, VerifyOtpView, SendAgainCodeView

urlpatterns = [
    path('register/', SignUpView.as_view()),
    path('verify_code/', VerifyOtpView.as_view()),
    path('send_again_code/', SendAgainCodeView.as_view())
]
