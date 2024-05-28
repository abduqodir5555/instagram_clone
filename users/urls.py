from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from users.views import SignUpView, VerifyOtpView, SendAgainCodeView, UserInformationView, PhotoStepView, LoginView, \
    AccountView, PasswordChangeView, ForgotPasswordView, ForgotPasswordVerifyView, ForgotPasswordChangeView

urlpatterns = [
    path('register/', SignUpView.as_view()),
    path('verify_code/', VerifyOtpView.as_view()),
    path('send_again_code/', SendAgainCodeView.as_view()),
    path('user_information/', UserInformationView.as_view()),
    path('photo-step/', PhotoStepView.as_view()),
    path('login/', LoginView.as_view()),
    path('account/', AccountView.as_view()),
    path('refresh-token/', TokenRefreshView.as_view()),
    path('logout/', TokenBlacklistView.as_view()),
    path('password-change/', PasswordChangeView.as_view()),

    path('forgot-password/', ForgotPasswordView.as_view()),
    path('forgot-password-verify/', ForgotPasswordVerifyView.as_view()),
    path('forgot-password-change/', ForgotPasswordChangeView.as_view()),
]
