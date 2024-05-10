from django.urls import path
from users.views import SignUpView, VerifyOtpView

urlpatterns = [
    path('register/', SignUpView.as_view()),
    path('verify_code/', VerifyOtpView.as_view())
]