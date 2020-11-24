import os
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from rest_framework import generics, status, mixins, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers import (
    UserSerializer,
    UpdateUserPasswordSerializer,
    LoginSerializer,
)


# hard coded first, but fix later once we have frontend
def send_verify_email_request(recepient, token, request):
    host = os.environ.get('{}_WEB_HOST'.format(settings.ENVVAR_PREFIX), 'http://localhost:3000')

    plaintext_content = """
        Welcome to [project name]!
        
        Please click following link to complete your sign in process.
        {host}/email-verification?email={email}&token={token}
        
        -------
        This email was sent to and contains information directly related to your account with us.
        Please do not reply to this message, as this email inbox is not monitored.
    """.format(host=host, email=recepient, token=token)

    html_content = render_to_string('user/email_verification.html', context={
        'host': host,
        'email': recepient,
        'token': token,
    })

    email = EmailMultiAlternatives('Activate your account', plaintext_content, to=[recepient])
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_password_change_email_request(recepient, token, request):
    host = os.environ.get('{}_WEB_HOST'.format(settings.ENVVAR_PREFIX), 'http://localhost:3000')
    body = '{host}/user/new-password/{recepient}/{token}'.format(host, recepient, token)
    email = EmailMessage('Activate your account', body, to=[recepient])
    email.send()


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LoginView(generics.GenericAPIView, mixins.CreateModelMixin):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data.get('user')
        login(request, user)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request):
        try:
            serializer = self.serializer_class(self.request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'updated': True,
                'user': serializer.validated_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 'updated': False, 'error': str(e) }, status=status.HTTP_400_BAD_REQUEST)


class SendUserVerificationEmailView(generics.GenericAPIView, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        email_verify_token, created = Token.objects.get_or_create(user=self.request.user)
        try:
            send_verify_email_request(request.user.email, email_verify_token.key, request)
            return Response(status=status.HTTP_200_OK)
        except:  # TODO: exception class를 구체화 해야 할 필요가 있음. (ex, SMTP 발송 실패)
            import traceback
            traceback.print_exc()
            return Response(status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmailView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        email = kwargs.get('email')
        user = Token.objects.get(key=token).user
        if user.email != email:
            return Response({ "error": "Invalid url" }, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()

        serializer = self.serializer_class(user)
        return Response(serializer.data)


class SendUserPasswordChangeEmailView(generics.GenericAPIView, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        passwordChangeToken = Token.objects.get_or_create(user=self.request.user)
        try:
            send_password_change_email_request(self.request.user.email, passwordChangeToken[0].key, request)
            return Response(status=status.HTTP_200_OK)
        except:  # TODO: exception class를 구체화 해야 할 필요가 있음. (ex, SMTP 발송 실패)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateUserPasswordView(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = get_user_model().objects.all()
    serializer_class = UpdateUserPasswordSerializer

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        email = kwargs.get('email')

        user = Token.objects.get(key=token).user
        if user.email != email:
            return Response({ "error": "Invalid url" }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class EmailCheckView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    def get(self, request):
        email = request.query_params.get('email')
        try:
            email = email.lower()
            validate_email(email)
        except:
            return Response({ 'available': False }, status=status.HTTP_400_BAD_REQUEST)
        if get_user_model().objects.filter(email=email).exists():
            return Response({ 'available': False }, status=status.HTTP_400_BAD_REQUEST)
        return Response({ 'available': True }, status=status.HTTP_200_OK)
