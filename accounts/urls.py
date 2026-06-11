# accounts/urls.py
from django.urls import path
from .views import (
    AdminUserDetailView,
    AdminUserListView,
    AdminUserStatutView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)

urlpatterns = [
    # Auth
    path('register/',  RegisterView.as_view(),  name='register'),
    path('login/',     LoginView.as_view(),      name='login'),
    path('logout/',    LogoutView.as_view(),      name='logout'),
    path('me/',        MeView.as_view(),          name='me'),

    # Admin — gestion des comptes
    path('admin/users/',               AdminUserListView.as_view(),   name='admin-users-list'),
    path('admin/users/<int:pk>/',      AdminUserDetailView.as_view(), name='admin-users-detail'),
    path('admin/users/<int:pk>/statut/', AdminUserStatutView.as_view(), name='admin-users-statut'),
]