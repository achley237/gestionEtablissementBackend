import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from establishments.models import Establishment, EstablishmentStatus, EstablishmentType
from .models import Comment, CommentStatus


@pytest.fixture
def utilisateur():
    return User.objects.create_user(
        email='comment-user@example.com',
        password='Password123!',
        nom='User',
        prenom='Comment',
        role=UserRole.UTILISATEUR,
    )


@pytest.fixture
def autre_utilisateur():
    return User.objects.create_user(
        email='other-comment-user@example.com',
        password='Password123!',
        nom='Other',
        prenom='Comment',
        role=UserRole.UTILISATEUR,
    )


@pytest.fixture
def directeur():
    return User.objects.create_user(
        email='comment-director@example.com',
        password='Password123!',
        nom='Director',
        prenom='Comment',
        role=UserRole.DIRECTEUR,
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email='comment-admin@example.com',
        password='Password123!',
        nom='Admin',
        prenom='Comment',
    )


@pytest.fixture
def published_establishment(directeur):
    return Establishment.objects.create(
        nom='College Note',
        type=EstablishmentType.SECONDAIRE,
        adresse='Rue 1',
        ville='Douala',
        region='Littoral',
        statut=EstablishmentStatus.PUBLIE,
        directeur=directeur,
    )


@pytest.fixture
def pending_establishment(directeur):
    return Establishment.objects.create(
        nom='College Attente',
        type=EstablishmentType.SECONDAIRE,
        adresse='Rue 2',
        ville='Douala',
        region='Littoral',
        statut=EstablishmentStatus.EN_ATTENTE,
        directeur=directeur,
    )


def comment_list_url(establishment):
    return reverse(
        'comments:establishment-comment-list',
        args=[establishment.id],
    )


@pytest.mark.django_db
def test_authenticated_user_can_comment_published_establishment(utilisateur, published_establishment):
    client = APIClient()
    client.force_authenticate(user=utilisateur)

    response = client.post(
        comment_list_url(published_establishment),
        {'contenu': 'Tres bon etablissement.', 'note': 5},
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['statut'] == CommentStatus.EN_ATTENTE
    assert response.data['auteur'] == utilisateur.id
    assert response.data['etablissement'] == published_establishment.id


@pytest.mark.django_db
def test_user_cannot_comment_same_establishment_twice(utilisateur, published_establishment):
    client = APIClient()
    client.force_authenticate(user=utilisateur)
    client.post(
        comment_list_url(published_establishment),
        {'contenu': 'Premier avis.', 'note': 4},
        format='json',
    )

    response = client.post(
        comment_list_url(published_establishment),
        {'contenu': 'Deuxieme avis.', 'note': 5},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Comment.objects.filter(
        auteur=utilisateur,
        etablissement=published_establishment,
    ).count() == 1


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(published_establishment):
    response = APIClient().post(
        comment_list_url(published_establishment),
        {'contenu': 'Avis visiteur.', 'note': 4},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_cannot_comment_unpublished_establishment(utilisateur, pending_establishment):
    client = APIClient()
    client.force_authenticate(user=utilisateur)

    response = client.post(
        comment_list_url(pending_establishment),
        {'contenu': 'Pas encore public.', 'note': 4},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_public_lists_only_approved_comments(utilisateur, autre_utilisateur, published_establishment):
    Comment.objects.create(
        auteur=utilisateur,
        etablissement=published_establishment,
        contenu='Visible',
        note=5,
        statut=CommentStatus.APPROUVE,
    )
    Comment.objects.create(
        auteur=autre_utilisateur,
        etablissement=published_establishment,
        contenu='Cache',
        note=2,
        statut=CommentStatus.EN_ATTENTE,
    )

    response = APIClient().get(comment_list_url(published_establishment))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['contenu'] == 'Visible'


@pytest.mark.django_db
def test_admin_can_approve_and_reject_comments(admin_user, utilisateur, published_establishment):
    comment = Comment.objects.create(
        auteur=utilisateur,
        etablissement=published_establishment,
        contenu='A moderer',
        note=3,
    )
    client = APIClient()
    client.force_authenticate(user=admin_user)

    approve_response = client.post(
        reverse('comments:comment-approve', args=[comment.id]),
        {},
        format='json',
    )
    reject_response = client.post(
        reverse('comments:comment-reject', args=[comment.id]),
        {'motif_rejet': 'Contenu non conforme'},
        format='json',
    )

    assert approve_response.status_code == status.HTTP_200_OK
    assert approve_response.data['statut'] == CommentStatus.APPROUVE
    assert reject_response.status_code == status.HTTP_200_OK
    assert reject_response.data['statut'] == CommentStatus.REJETE
    assert reject_response.data['motif_rejet'] == 'Contenu non conforme'


@pytest.mark.django_db
def test_rating_uses_only_approved_comments(utilisateur, autre_utilisateur, published_establishment):
    Comment.objects.create(
        auteur=utilisateur,
        etablissement=published_establishment,
        contenu='Top',
        note=5,
        statut=CommentStatus.APPROUVE,
    )
    Comment.objects.create(
        auteur=autre_utilisateur,
        etablissement=published_establishment,
        contenu='Moyen',
        note=3,
        statut=CommentStatus.APPROUVE,
    )
    pending_user = User.objects.create_user(
        email='pending-note@example.com',
        password='Password123!',
        nom='Pending',
        prenom='Note',
    )
    Comment.objects.create(
        auteur=pending_user,
        etablissement=published_establishment,
        contenu='Pas encore modere',
        note=1,
        statut=CommentStatus.EN_ATTENTE,
    )

    response = APIClient().get(
        reverse('comments:establishment-comment-rating', args=[published_establishment.id])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['note_moyenne'] == 4
    assert response.data['total_commentaires'] == 2
