from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .base import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves new user
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=email.lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves new superuser
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_verified = models.BooleanField(
        _('email verification status'),
        default=False,
        help_text=_(
            'Designates whether this user has verified email. '
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        db_table = 'account_users'
        
    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class SignupRouteCategory(BaseModel):
    name = models.CharField(
        _('name'),
        max_length=200,
    )

    class Meta:
        db_table = 'account_signup_route_category'

    def __str__(self):
        return self.name


class UserRouteMap(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routes')
    category = models.ForeignKey(
        SignupRouteCategory,
        on_delete=models.CASCADE,
    )
    description = models.CharField(
        _('description'),
        max_length=200,
    )

    class Meta:
        db_table = 'account_user_route_map'


class DropoutReasonCategory(BaseModel):
    name = models.CharField(
        _('name'),
        max_length=200,
    )

    class Meta:
        db_table = 'account_dropout_reason_category'

    def __str__(self):
        return self.name


class UserDropoutReasonMap(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dropout_reasons')
    category = models.ForeignKey(
        DropoutReasonCategory,
        on_delete=models.CASCADE,
    )
    description = models.CharField(
        _('description'),
        max_length=200,
    )

    class Meta:
        db_table = 'account_user_dropout_reason_map'
