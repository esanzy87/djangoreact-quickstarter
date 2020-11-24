from rest_framework import routers
from .user import (
    RegisterView,
    LoginView,
    MeView,
    SendUserVerificationEmailView,
    VerifyUserEmailView,
    SendUserPasswordChangeEmailView,
    UpdateUserPasswordView,
    EmailCheckView,
)


router = routers.DefaultRouter()
