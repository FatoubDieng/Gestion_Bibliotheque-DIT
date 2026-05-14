from django.urls import path, include

urlpatterns = [
    path('api/', include('livres_app.urls')),
]