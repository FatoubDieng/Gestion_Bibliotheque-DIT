from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivreViewSet

router = DefaultRouter()
router.register(r'livres', LivreViewSet, basename='livre')

urlpatterns = [
    path('', include(router.urls)),
    # Health check
    path('health/', lambda request: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok', 'service': 'livres'})),
]