from rest_framework.routers import DefaultRouter

from .views import EstablishmentViewSet

app_name = 'establishments'

router = DefaultRouter()
router.register('', EstablishmentViewSet, basename='establishment')

urlpatterns = router.urls
