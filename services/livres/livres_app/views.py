from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Livre
from .serializers import LivreSerializer, LivreListSerializer


class LivreViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour la gestion des livres.

    Endpoints générés automatiquement :
      GET    /api/livres/           → liste tous les livres
      POST   /api/livres/           → ajouter un livre
      GET    /api/livres/{id}/      → détail d'un livre
      PUT    /api/livres/{id}/      → modifier un livre
      PATCH  /api/livres/{id}/      → modification partielle
      DELETE /api/livres/{id}/      → supprimer un livre

    Endpoints personnalisés :
      GET    /api/livres/search/         → recherche multi-critères
      GET    /api/livres/disponibles/    → livres disponibles
      GET    /api/livres/categories/     → liste des catégories
      POST   /api/livres/{id}/emprunter/ → décrémenter le stock
      POST   /api/livres/{id}/retourner/ → incrémenter le stock
    """
    queryset = Livre.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['titre', 'auteur', 'categorie', 'annee', 'stock_dispo']
    ordering = ['titre']

    def get_serializer_class(self):
        if self.action == 'list':
            return LivreListSerializer
        return LivreSerializer

    # ── Endpoint 1 : Recherche multi-critères ──────────────────
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        GET /api/livres/search/?q=python
        GET /api/livres/search/?titre=clean&auteur=martin
        GET /api/livres/search/?isbn=978-0132350884
        """
        q       = request.query_params.get('q', '')
        titre   = request.query_params.get('titre', '')
        auteur  = request.query_params.get('auteur', '')
        isbn    = request.query_params.get('isbn', '')
        categorie = request.query_params.get('categorie', '')

        queryset = Livre.objects.all()

        if q:
            queryset = queryset.filter(
                Q(titre__icontains=q) |
                Q(auteur__icontains=q) |
                Q(isbn__icontains=q) |
                Q(description__icontains=q)
            )
        if titre:
            queryset = queryset.filter(titre__icontains=titre)
        if auteur:
            queryset = queryset.filter(auteur__icontains=auteur)
        if isbn:
            queryset = queryset.filter(isbn__icontains=isbn)
        if categorie:
            queryset = queryset.filter(categorie__icontains=categorie)

        serializer = LivreListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'query': {'q': q, 'titre': titre, 'auteur': auteur, 'isbn': isbn},
            'results': serializer.data
        })

    # ── Endpoint 2 : Livres disponibles ───────────────────────
    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        """GET /api/livres/disponibles/ → livres avec stock_dispo > 0"""
        queryset = Livre.objects.filter(stock_dispo__gt=0)
        serializer = LivreListSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    # ── Endpoint 3 : Liste des catégories ──────────────────────
    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        """GET /api/livres/categories/ → liste unique des catégories"""
        categories = (
            Livre.objects.exclude(categorie='')
            .values_list('categorie', flat=True)
            .distinct()
            .order_by('categorie')
        )
        return Response({'categories': list(categories)})

    # ── Endpoint 4 : Emprunter (décrémenter stock) ─────────────
    @action(detail=True, methods=['post'], url_path='emprunter')
    def emprunter(self, request, pk=None):
        """
        POST /api/livres/{id}/emprunter/
        Appelé par le service Emprunts pour décrémenter le stock.
        """
        livre = self.get_object()
        if livre.stock_dispo <= 0:
            return Response(
                {'error': f'Le livre "{livre.titre}" n\'est plus disponible.'},
                status=status.HTTP_409_CONFLICT
            )
        livre.stock_dispo -= 1
        livre.save(update_fields=['stock_dispo', 'updated_at'])
        return Response({
            'message': 'Stock décrémenté avec succès.',
            'livre_id': livre.id,
            'stock_dispo': livre.stock_dispo
        })

    # ── Endpoint 5 : Retourner (incrémenter stock) ─────────────
    @action(detail=True, methods=['post'], url_path='retourner')
    def retourner(self, request, pk=None):
        """
        POST /api/livres/{id}/retourner/
        Appelé par le service Emprunts lors du retour d'un livre.
        """
        livre = self.get_object()
        if livre.stock_dispo >= livre.stock_total:
            return Response(
                {'error': 'Le stock est déjà au maximum.'},
                status=status.HTTP_409_CONFLICT
            )
        livre.stock_dispo += 1
        livre.save(update_fields=['stock_dispo', 'updated_at'])
        return Response({
            'message': 'Stock incrémenté avec succès.',
            'livre_id': livre.id,
            'stock_dispo': livre.stock_dispo
        })