from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import UtilisateurViewSet

router = DefaultRouter()
router.register(r'users', UtilisateurViewSet, basename='utilisateur')


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'users'})


urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check),
]
