from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import EmpruntViewSet

router = DefaultRouter()
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'emprunts'})


urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check),
]
