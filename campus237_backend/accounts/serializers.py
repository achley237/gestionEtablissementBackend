from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserRole, UserStatus


class UserSerializer(serializers.ModelSerializer):
    redirect_to = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'nom',
            'prenom',
            'email',
            'role',
            'statut',
            'fonction',
            'niveau_acces',
            'date_inscription',
            'redirect_to',
        )
        read_only_fields = ('id', 'statut', 'niveau_acces', 'date_inscription')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=(UserRole.UTILISATEUR, UserRole.DIRECTEUR),
        default=UserRole.UTILISATEUR,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'nom',
            'prenom',
            'email',
            'password',
            'password_confirm',
            'role',
            'fonction',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )

        if user is None:
            raise AuthenticationFailed('Identifiants invalides.')
        if user.statut != UserStatus.ACTIF or not user.is_active:
            raise PermissionDenied('Ce compte est suspendu ou banni.')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'redirect_to': user.redirect_to,
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()
