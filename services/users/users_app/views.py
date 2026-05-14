from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.http import JsonResponse

from .models import Utilisateur
from .serializers import (
    UtilisateurSerializer,
    UtilisateurListSerializer,
    UtilisateurProfilSerializer,
)


class UtilisateurViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour la gestion des utilisateurs.

    Endpoints automatiques :
      GET    /api/users/              → liste tous les utilisateurs
      POST   /api/users/              → créer un utilisateur
      GET    /api/users/{id}/         → détail d'un utilisateur
      PUT    /api/users/{id}/         → modifier un utilisateur
      PATCH  /api/users/{id}/         → modification partielle
      DELETE /api/users/{id}/         → supprimer un utilisateur

    Endpoints personnalisés :
      GET  /api/users/par-type/          → filtrer par type (etudiant/professeur/personnel)
      GET  /api/users/{id}/profil/       → profil complet de l'utilisateur
      GET  /api/users/search/            → recherche par nom, email, matricule
      POST /api/users/{id}/activer/      → activer un compte
      POST /api/users/{id}/desactiver/   → désactiver un compte
      GET  /api/users/statistiques/      → stats globales des utilisateurs
    """

    queryset = Utilisateur.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nom', 'prenom', 'type_user', 'created_at']
    ordering = ['nom', 'prenom']

    def get_serializer_class(self):
        if self.action == 'list':
            return UtilisateurListSerializer
        if self.action == 'profil':
            return UtilisateurProfilSerializer
        return UtilisateurSerializer

    # Endpoint 1 : Filtrer par type 
    @action(detail=False, methods=['get'], url_path='par-type')
    def par_type(self, request):
        """
        GET /api/users/par-type/?type=etudiant
        GET /api/users/par-type/?type=professeur
        GET /api/users/par-type/?type=personnel

        Retourne la liste des utilisateurs filtrée par type.
        Si pas de paramètre → retourne tous les types groupés.
        """
        type_user = request.query_params.get('type', '').lower()

        types_valides = ['etudiant', 'professeur', 'personnel']

        if type_user and type_user not in types_valides:
            return Response(
                {
                    'error': f"Type invalide : '{type_user}'.",
                    'types_valides': types_valides
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if type_user:
            # Filtrer par type spécifique
            queryset = Utilisateur.objects.filter(type_user=type_user)
            serializer = UtilisateurListSerializer(queryset, many=True)
            return Response({
                'type': type_user,
                'count': queryset.count(),
                'results': serializer.data
            })
        else:
            # Retourner tous les types groupés
            result = {}
            for t in types_valides:
                qs = Utilisateur.objects.filter(type_user=t)
                result[t] = {
                    'count': qs.count(),
                    'utilisateurs': UtilisateurListSerializer(qs, many=True).data
                }
            return Response(result)

    # ── Endpoint 2 : Profil complet ────────────────────────────
    @action(detail=True, methods=['get'], url_path='profil')
    def profil(self, request, pk=None):
        """
        GET /api/users/{id}/profil/
        Retourne le profil détaillé d'un utilisateur.
        """
        utilisateur = self.get_object()
        serializer = UtilisateurProfilSerializer(utilisateur)
        return Response(serializer.data)

    # ── Endpoint 3 : Recherche ─────────────────────────────────
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        GET /api/users/search/?q=amadou
        GET /api/users/search/?email=amadou@dit.sn
        GET /api/users/search/?matricule=ETU-2024-001
        """
        q          = request.query_params.get('q', '')
        email      = request.query_params.get('email', '')
        matricule  = request.query_params.get('matricule', '')

        queryset = Utilisateur.objects.all()

        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) |
                Q(prenom__icontains=q) |
                Q(email__icontains=q) |
                Q(matricule__icontains=q)
            )
        if email:
            queryset = queryset.filter(email__icontains=email)
        if matricule:
            queryset = queryset.filter(matricule__icontains=matricule)

        serializer = UtilisateurListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'query': {'q': q, 'email': email, 'matricule': matricule},
            'results': serializer.data
        })

    # ── Endpoint 4 : Activer un compte ────────────────────────
    @action(detail=True, methods=['post'], url_path='activer')
    def activer(self, request, pk=None):
        """
        POST /api/users/{id}/activer/
        Active le compte d'un utilisateur désactivé.
        """
        utilisateur = self.get_object()

        if utilisateur.actif:
            return Response(
                {'message': f"{utilisateur.nom_complet} est déjà actif."},
                status=status.HTTP_200_OK
            )

        utilisateur.actif = True
        utilisateur.save(update_fields=['actif', 'updated_at'])

        return Response({
            'message': f"Compte de {utilisateur.nom_complet} activé avec succès.",
            'utilisateur_id': utilisateur.id,
            'actif': utilisateur.actif
        })

    # ── Endpoint 5 : Désactiver un compte ─────────────────────
    @action(detail=True, methods=['post'], url_path='desactiver')
    def desactiver(self, request, pk=None):
        """
        POST /api/users/{id}/desactiver/
        Désactive le compte (soft delete — l'utilisateur reste en DB).
        """
        utilisateur = self.get_object()

        if not utilisateur.actif:
            return Response(
                {'message': f"{utilisateur.nom_complet} est déjà désactivé."},
                status=status.HTTP_200_OK
            )

        utilisateur.actif = False
        utilisateur.save(update_fields=['actif', 'updated_at'])

        return Response({
            'message': f"Compte de {utilisateur.nom_complet} désactivé.",
            'utilisateur_id': utilisateur.id,
            'actif': utilisateur.actif
        })

    # ── Endpoint 6 : Statistiques ──────────────────────────────
    @action(detail=False, methods=['get'], url_path='statistiques')
    def statistiques(self, request):
        """
        GET /api/users/statistiques/
        Retourne les statistiques globales sur les utilisateurs.
        """
        total      = Utilisateur.objects.count()
        actifs     = Utilisateur.objects.filter(actif=True).count()
        inactifs   = Utilisateur.objects.filter(actif=False).count()
        etudiants  = Utilisateur.objects.filter(type_user='etudiant').count()
        profs      = Utilisateur.objects.filter(type_user='professeur').count()
        personnel  = Utilisateur.objects.filter(type_user='personnel').count()

        return Response({
            'total': total,
            'actifs': actifs,
            'inactifs': inactifs,
            'par_type': {
                'etudiants': etudiants,
                'professeurs': profs,
                'personnel': personnel,
            }
        })
