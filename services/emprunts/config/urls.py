from django.urls import path, include

urlpatterns = [
    path('api/', include('emprunts_app.urls')),
]