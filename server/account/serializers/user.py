from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    tokens = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'password', 'email', 'date_joined', 'last_login',
            'is_superuser', 'is_active', 'is_staff', 'tokens',
        )
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def validate_email(self, value):
        norm_email = value.lower()
        if get_user_model().objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("Not unique email")
        return norm_email


class UpdateUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='login')
        attrs['user'] = user
        return attrs
