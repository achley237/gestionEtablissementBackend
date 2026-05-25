import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import User, UserRole, UserStatus


@pytest.mark.django_db
def test_register_creates_utilisateur_by_default():
    client = APIClient()
    response = client.post(reverse('accounts:register'), {
        'nom': 'Ngono',
        'prenom': 'Alice',
        'email': 'alice@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!',
    }, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['role'] == UserRole.UTILISATEUR
    assert response.data['redirect_to'] == '/dashboard/utilisateur'
    assert User.objects.filter(email='alice@example.com').exists()


@pytest.mark.django_db
def test_register_directeur_keeps_function():
    client = APIClient()
    response = client.post(reverse('accounts:register'), {
        'nom': 'Talla',
        'prenom': 'Marc',
        'email': 'marc@example.com',
        'password': 'Password123!',
        'password_confirm': 'Password123!',
        'role': UserRole.DIRECTEUR,
        'fonction': 'Directeur general',
    }, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['role'] == UserRole.DIRECTEUR
    assert response.data['fonction'] == 'Directeur general'
    assert response.data['redirect_to'] == '/dashboard/directeur'


@pytest.mark.django_db
def test_login_returns_jwt_tokens_and_role_redirect():
    client = APIClient()
    User.objects.create_user(
        email='directeur@example.com',
        password='Password123!',
        nom='Meka',
        prenom='Jeanne',
        role=UserRole.DIRECTEUR,
    )

    response = client.post(reverse('accounts:login'), {
        'email': 'directeur@example.com',
        'password': 'Password123!',
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['access']
    assert response.data['refresh']
    assert response.data['redirect_to'] == '/dashboard/directeur'


@pytest.mark.django_db
def test_admin_login_redirects_to_admin_dashboard():
    client = APIClient()
    User.objects.create_superuser(
        email='admin@example.com',
        password='Password123!',
        nom='Admin',
        prenom='Campus',
    )

    response = client.post(reverse('accounts:login'), {
        'email': 'admin@example.com',
        'password': 'Password123!',
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['user']['role'] == UserRole.ADMIN
    assert response.data['redirect_to'] == '/dashboard/admin'


@pytest.mark.django_db
def test_login_rejects_suspended_account():
    client = APIClient()
    User.objects.create_user(
        email='blocked@example.com',
        password='Password123!',
        nom='Blocked',
        prenom='User',
        statut=UserStatus.SUSPENDU,
    )

    response = client.post(reverse('accounts:login'), {
        'email': 'blocked@example.com',
        'password': 'Password123!',
    }, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_login_rejects_bad_credentials_with_401():
    client = APIClient()

    response = client.post(reverse('accounts:login'), {
        'email': 'missing@example.com',
        'password': 'Password123!',
    }, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_requires_authentication_and_returns_current_user():
    client = APIClient()
    user = User.objects.create_user(
        email='me@example.com',
        password='Password123!',
        nom='Essomba',
        prenom='Paul',
    )
    client.force_authenticate(user=user)

    response = client.get(reverse('accounts:me'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'me@example.com'
