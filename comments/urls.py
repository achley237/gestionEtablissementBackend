from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminCommentViewSet, EstablishmentCommentViewSet

app_name = 'comments'

admin_router = DefaultRouter()
admin_router.register('', AdminCommentViewSet, basename='comment')

establishment_comments = EstablishmentCommentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
establishment_comment_detail = EstablishmentCommentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',
})
establishment_rating = EstablishmentCommentViewSet.as_view({
    'get': 'rating',
})

urlpatterns = [
    path('', include(admin_router.urls)),
    path(
        'etablissements/<int:establishment_pk>/commentaires/',
        establishment_comments,
        name='establishment-comment-list',
    ),
    path(
        'etablissements/<int:establishment_pk>/commentaires/rating/',
        establishment_rating,
        name='establishment-comment-rating',
    ),
    path(
        'etablissements/<int:establishment_pk>/commentaires/<int:pk>/',
        establishment_comment_detail,
        name='establishment-comment-detail',
    ),
]
