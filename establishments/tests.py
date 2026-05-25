import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserRole
from .models import Establishment, EstablishmentStatus, EstablishmentType


def establishment_payload(**overrides):
    payload = {
        'nom': 'College Bilingue Campus237',
        'type': EstablishmentType.SECONDAIRE,
        'adresse': 'Rue 12, Bonamoussadi',
        'ville': 'Douala',
        'region': 'Littoral',
        'pays': 'Cameroun',
        'telephone': '+237699000000',
        'email': 'contact@campus237.cm',
        'site_web': 'https://campus237.cm',
        'niveaux_scolaires': ['6eme', '5eme', '4eme'],
        'capacite': 800,
        'annee_creation': 2010,
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def utilisateur():
    return User.objects.create_user(
        email='user@example.com',
        password='Password123!',
        nom='User',
        prenom='Simple',
        role=UserRole.UTILISATEUR,
    )


@pytest.fixture
def directeur():
    return User.objects.create_user(
        email='directeur@example.com',
        password='Password123!',
        nom='Directeur',
        prenom='Marie',
        role=UserRole.DIRECTEUR,
    )


@pytest.fixture
def autre_directeur():
    return User.objects.create_user(
        email='autre@example.com',
        password='Password123!',
        nom='Autre',
        prenom='Jean',
        role=UserRole.DIRECTEUR,
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email='admin-etab@example.com',
        password='Password123!',
        nom='Admin',
        prenom='Root',
    )


@pytest.mark.django_db
def test_visiteur_can_list_only_published_establishments(directeur):
    Establishment.objects.create(
        **establishment_payload(nom='Publie', statut=EstablishmentStatus.PUBLIE),
        directeur=directeur,
    )
    Establishment.objects.create(
        **establishment_payload(nom='En attente', statut=EstablishmentStatus.EN_ATTENTE),
        directeur=directeur,
    )

    response = APIClient().get(reverse('establishments:establishment-list'))

    assert response.status_code == status.HTTP_200_OK
    assert [item['nom'] for item in response.data] == ['Publie']


@pytest.mark.django_db
def test_directeur_can_create_establishment_in_pending_status(directeur):
    client = APIClient()
    client.force_authenticate(user=directeur)

    response = client.post(
        reverse('establishments:establishment-list'),
        establishment_payload(),
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['statut'] == EstablishmentStatus.EN_ATTENTE
    assert response.data['directeur'] == directeur.id


@pytest.mark.django_db
def test_utilisateur_cannot_create_establishment(utilisateur):
    client = APIClient()
    client.force_authenticate(user=utilisateur)

    response = client.post(
        reverse('establishments:establishment-list'),
        establishment_payload(),
        format='json',
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_directeur_can_update_only_own_establishment(directeur, autre_directeur):
    own = Establishment.objects.create(
        **establishment_payload(nom='A moi', statut=EstablishmentStatus.EN_ATTENTE),
        directeur=directeur,
    )
    other = Establishment.objects.create(
        **establishment_payload(nom='A autre', statut=EstablishmentStatus.EN_ATTENTE),
        directeur=autre_directeur,
    )
    client = APIClient()
    client.force_authenticate(user=directeur)

    own_response = client.patch(
        reverse('establishments:establishment-detail', args=[own.id]),
        {'ville': 'Yaounde'},
        format='json',
    )
    other_response = client.patch(
        reverse('establishments:establishment-detail', args=[other.id]),
        {'ville': 'Bafoussam'},
        format='json',
    )

    assert own_response.status_code == status.HTTP_200_OK
    assert own_response.data['ville'] == 'Yaounde'
    assert other_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_admin_create_publishes_immediately_and_can_approve_reject(admin_user, directeur):
    pending = Establishment.objects.create(
        **establishment_payload(nom='A valider', statut=EstablishmentStatus.EN_ATTENTE),
        directeur=directeur,
    )
    client = APIClient()
    client.force_authenticate(user=admin_user)

    create_response = client.post(
        reverse('establishments:establishment-list'),
        establishment_payload(nom='Cree par admin'),
        format='json',
    )
    approve_response = client.post(
        reverse('establishments:establishment-approve', args=[pending.id]),
        {},
        format='json',
    )
    reject_response = client.post(
        reverse('establishments:establishment-reject', args=[pending.id]),
        {'motif_rejet': 'Informations incompletes'},
        format='json',
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert create_response.data['statut'] == EstablishmentStatus.PUBLIE
    assert approve_response.status_code == status.HTTP_200_OK
    assert approve_response.data['statut'] == EstablishmentStatus.PUBLIE
    assert reject_response.status_code == status.HTTP_200_OK
    assert reject_response.data['statut'] == EstablishmentStatus.REJETE
    assert reject_response.data['motif_rejet'] == 'Informations incompletes'


@pytest.mark.django_db
def test_search_filters_by_city_and_type(directeur):
    Establishment.objects.create(
        **establishment_payload(nom='Douala College', ville='Douala', type=EstablishmentType.SECONDAIRE, statut=EstablishmentStatus.PUBLIE),
        directeur=directeur,
    )
    Establishment.objects.create(
        **establishment_payload(nom='Yaounde University', ville='Yaounde', type=EstablishmentType.UNIVERSITE, statut=EstablishmentStatus.PUBLIE),
        directeur=directeur,
    )

    response = APIClient().get(
        reverse('establishments:establishment-list'),
        {'ville': 'Douala', 'type': EstablishmentType.SECONDAIRE},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nom'] == 'Douala College'


@pytest.mark.django_db
def test_public_search_returns_count_results_and_only_published(directeur):
    Establishment.objects.create(
        **establishment_payload(
            nom='Institut Primaire Akwa',
            ville='Douala',
            type=EstablishmentType.PRIMAIRE,
            niveaux_scolaires=['Sil', 'CP'],
            statut=EstablishmentStatus.PUBLIE,
        ),
        directeur=directeur,
    )
    Establishment.objects.create(
        **establishment_payload(
            nom='Institut Prive Cache',
            ville='Douala',
            type=EstablishmentType.PRIMAIRE,
            statut=EstablishmentStatus.EN_ATTENTE,
        ),
        directeur=directeur,
    )

    response = APIClient().get(
        reverse('establishments:establishment-search'),
        {'q': 'institut', 'ville': 'Douala', 'niveau': 'CP'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['criteres']['q'] == 'institut'
    assert response.data['results'][0]['nom'] == 'Institut Primaire Akwa'


@pytest.mark.django_db
def test_public_search_supports_numeric_ranges_and_ordering(directeur):
    Establishment.objects.create(
        **establishment_payload(
            nom='Petit College',
            capacite=300,
            annee_creation=2001,
            statut=EstablishmentStatus.PUBLIE,
        ),
        directeur=directeur,
    )
    Establishment.objects.create(
        **establishment_payload(
            nom='Grand Lycee',
            capacite=1500,
            annee_creation=1995,
            statut=EstablishmentStatus.PUBLIE,
        ),
        directeur=directeur,
    )
    Establishment.objects.create(
        **establishment_payload(
            nom='Universite Moyenne',
            capacite=900,
            annee_creation=2018,
            statut=EstablishmentStatus.PUBLIE,
        ),
        directeur=directeur,
    )

    response = APIClient().get(
        reverse('establishments:establishment-search'),
        {
            'capacite_min': '500',
            'capacite_max': '1600',
            'annee_creation_max': '2018',
            'ordering': '-capacite',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert [item['nom'] for item in response.data['results']] == [
        'Grand Lycee',
        'Universite Moyenne',
    ]


@pytest.mark.django_db
def test_public_cannot_retrieve_unpublished_establishment(directeur):
    pending = Establishment.objects.create(
        **establishment_payload(statut=EstablishmentStatus.EN_ATTENTE),
        directeur=directeur,
    )

    response = APIClient().get(
        reverse('establishments:establishment-detail', args=[pending.id])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
