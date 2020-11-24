"""
URLs for core app
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    router,
    RegisterView,
    LoginView,
    MeView,
    SendUserVerificationEmailView,
    VerifyUserEmailView,
    SendUserPasswordChangeEmailView,
    UpdateUserPasswordView,
    EmailCheckView,
)


app_name = 'account'


urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('request-email-verification/', SendUserVerificationEmailView.as_view(), name='request-email-verification'),
    path('email-verify/<str:email>/<str:token>/', VerifyUserEmailView.as_view(), name='email-verify'),
    path('reset-password/', SendUserPasswordChangeEmailView.as_view(), name='reset-password'),
    path('new-password/<str:email>/<str:token>', UpdateUserPasswordView.as_view(), name='new-password'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
