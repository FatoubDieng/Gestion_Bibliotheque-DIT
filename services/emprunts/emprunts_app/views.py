"""
Ce service  :
  1. Vérifie la disponibilité du livre  ( Service Livres)
  2. Vérifie que l'utilisateur est actif ( Service Users)
  3. Gère le cycle de vie des emprunts
  4. Détecte les retards automatiquement
  5. Exporte les données pour le modèle ML
"""
import csv
import os
from datetime import date

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Emprunt
from .serializers import (
    EmpruntSerializer,
    EmpruntCreateSerializer,
    EmpruntListSerializer,
    RetourSerializer,
)
from .services import ServiceLivresClient, ServiceUsersClient


class EmpruntViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour la gestion des emprunts.

    Endpoints automatiques :
      GET    /api/emprunts/          → liste tous les emprunts
      GET    /api/emprunts/{id}/     → détail d'un emprunt
      DELETE /api/emprunts/{id}/     → supprimer un emprunt

    Endpoints personnalisés :
      POST /api/emprunts/emprunter/          → créer un emprunt
      POST /api/emprunts/{id}/retourner/     → retourner un livre
      GET  /api/emprunts/historique/         → historique avec filtres
      GET  /api/emprunts/retards/            → tous les emprunts en retard
      POST /api/emprunts/detecter-retards/   → mettre à jour les statuts
      GET  /api/emprunts/export-csv/         → export pour ML
      GET  /api/emprunts/statistiques/       → stats globales
    """

    queryset = Emprunt.objects.all().order_by('-date_emprunt')

    def get_serializer_class(self):
        if self.action == 'emprunter':
            return EmpruntCreateSerializer
        if self.action == 'retourner':
            return RetourSerializer
        if self.action == 'list':
            return EmpruntListSerializer
        return EmpruntSerializer

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 1 : Emprunter un livre
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['post'], url_path='emprunter')
    def emprunter(self, request):
        """
        POST /api/emprunts/emprunter/
        Body: { "utilisateur_id": 1, "livre_id": 3 }

        Processus :
          1. Valider les données reçues
          2. Vérifier que l'utilisateur existe et est actif
          3. Vérifier que le livre existe et est disponible
          4. Créer l'emprunt en DB
          5. Notifier le service Livres de décrémenter le stock
        """
        serializer = EmpruntCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        utilisateur_id = serializer.validated_data['utilisateur_id']
        livre_id       = serializer.validated_data['livre_id']

        # ── Étape 2 : Vérifier l'utilisateur ─────────────────────
        users_client = ServiceUsersClient()
        user_ok, user_msg = users_client.verifier_utilisateur(utilisateur_id)
        if not user_ok:
            return Response({'error': user_msg}, status=status.HTTP_404_NOT_FOUND)

        # ── Étape 3 : Vérifier le livre ───────────────────────────
        livres_client = ServiceLivresClient()
        livre_ok, livre_msg = livres_client.verifier_disponibilite(livre_id)
        if not livre_ok:
            return Response({'error': livre_msg}, status=status.HTTP_409_CONFLICT)

        # ── Étape 4 : Créer l'emprunt ─────────────────────────────
        emprunt = serializer.save()

        # ── Étape 5 : Décrémenter le stock ────────────────────────
        stock_ok = livres_client.decrementer_stock(livre_id)
        if not stock_ok:
            # Rollback : supprimer l'emprunt si le stock n'a pas pu être décrémenté
            emprunt.delete()
            return Response(
                {'error': 'Impossible de mettre à jour le stock. Réessayez.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            EmpruntSerializer(emprunt).data,
            status=status.HTTP_201_CREATED
        )

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 2 : Retourner un livre
    # ═══════════════════════════════════════════════════════════════
    @action(detail=True, methods=['post'], url_path='retourner')
    def retourner(self, request, pk=None):
        """
        POST /api/emprunts/{id}/retourner/
        Body (optionnel): { "note_utilisateur": 4, "commentaire": "Excellent livre" }

        Processus :
          1. Vérifier que l'emprunt existe et n'est pas déjà retourné
          2. Marquer comme retourné avec la date du jour
          3. Notifier le service Livres d'incrémenter le stock
        """
        emprunt = self.get_object()

        if emprunt.statut == Emprunt.Statut.RETOURNE:
            return Response(
                {'error': 'Ce livre a déjà été retourné.'},
                status=status.HTTP_409_CONFLICT
            )

        # Récupérer la note et le commentaire si fournis
        serializer = RetourSerializer(data=request.data)
        if serializer.is_valid():
            emprunt.note_utilisateur = serializer.validated_data.get('note_utilisateur')
            emprunt.commentaire      = serializer.validated_data.get('commentaire', '')

        # Mettre à jour le statut
        emprunt.date_retour_reel = timezone.now().date()
        emprunt.statut           = Emprunt.Statut.RETOURNE
        emprunt.save()

        # Incrémenter le stock dans le service Livres
        livres_client = ServiceLivresClient()
        livres_client.incrementer_stock(emprunt.livre_id)

        return Response({
            'message': 'Livre retourné avec succès.',
            'emprunt': EmpruntSerializer(emprunt).data
        })

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 3 : Historique avec filtres
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['get'], url_path='historique')
    def historique(self, request):
        """
        GET /api/emprunts/historique/
        GET /api/emprunts/historique/?utilisateur_id=1
        GET /api/emprunts/historique/?livre_id=3
        GET /api/emprunts/historique/?statut=en_cours
        GET /api/emprunts/historique/?date_debut=2024-01-01&date_fin=2024-12-31
        """
        queryset = Emprunt.objects.all().order_by('-date_emprunt')

        # Filtres
        utilisateur_id = request.query_params.get('utilisateur_id')
        livre_id       = request.query_params.get('livre_id')
        statut         = request.query_params.get('statut')
        date_debut     = request.query_params.get('date_debut')
        date_fin       = request.query_params.get('date_fin')

        if utilisateur_id:
            queryset = queryset.filter(utilisateur_id=utilisateur_id)
        if livre_id:
            queryset = queryset.filter(livre_id=livre_id)
        if statut:
            queryset = queryset.filter(statut=statut)
        if date_debut:
            queryset = queryset.filter(date_emprunt__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_emprunt__lte=date_fin)

        serializer = EmpruntListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'filtres': {
                'utilisateur_id': utilisateur_id,
                'livre_id': livre_id,
                'statut': statut,
            },
            'results': serializer.data
        })

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 4 : Emprunts en retard
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['get'], url_path='retards')
    def retards(self, request):
        """
        GET /api/emprunts/retards/
        Retourne tous les emprunts dont la date de retour est dépassée.
        """
        aujourd_hui = timezone.now().date()
        retards = Emprunt.objects.filter(
            statut__in=[Emprunt.Statut.EN_COURS, Emprunt.Statut.EN_RETARD],
            date_retour_prevue__lt=aujourd_hui
        ).order_by('date_retour_prevue')

        serializer = EmpruntSerializer(retards, many=True)
        return Response({
            'count': retards.count(),
            'date_verification': str(aujourd_hui),
            'retards': serializer.data
        })

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 5 : Détecter et mettre à jour les retards
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['post'], url_path='detecter-retards')
    def detecter_retards(self, request):
        """
        POST /api/emprunts/detecter-retards/
        Met à jour le statut de tous les emprunts en retard.
        À appeler régulièrement (cron job).
        """
        aujourd_hui = timezone.now().date()

        # Trouver tous les emprunts EN_COURS dont la date est dépassée
        emprunts_a_mettre_a_jour = Emprunt.objects.filter(
            statut=Emprunt.Statut.EN_COURS,
            date_retour_prevue__lt=aujourd_hui
        )

        count = emprunts_a_mettre_a_jour.count()
        emprunts_a_mettre_a_jour.update(statut=Emprunt.Statut.EN_RETARD)

        return Response({
            'message': f'{count} emprunt(s) mis à jour en statut EN_RETARD.',
            'count': count,
            'date': str(aujourd_hui)
        })

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 6 : Export CSV pour le Machine Learning
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        """
        GET /api/emprunts/export-csv/
        Exporte l'historique des emprunts au format CSV pour le ML.

        Format CSV produit :
          user_id, book_id, rating, date_emprunt, duree_jours

        Le 'rating' est :
          - La note de l'utilisateur si elle existe (1-5)
          - Sinon 3 par défaut (neutre)

        Ce fichier devient loans.csv pour DVC.
        """
        emprunts = Emprunt.objects.filter(
            statut=Emprunt.Statut.RETOURNE
        ).order_by('utilisateur_id', 'livre_id')

        # ── Option 1 : Téléchargement direct HTTP ─────────────────
        if request.query_params.get('download') == 'true':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="loans.csv"'
            writer = csv.writer(response)
            writer.writerow(['user_id', 'book_id', 'rating', 'date_emprunt', 'duree_jours'])
            for e in emprunts:
                writer.writerow([
                    e.utilisateur_id,
                    e.livre_id,
                    e.note_utilisateur if e.note_utilisateur else 3,
                    str(e.date_emprunt),
                    e.duree_emprunt
                ])
            return response

        # ── Option 2 : Sauvegarder sur disque (pour DVC) ──────────
        export_dir = getattr(settings, 'EXPORT_DIR', '/app/exports')
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, 'loans.csv')

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'book_id', 'rating', 'date_emprunt', 'duree_jours'])
            for e in emprunts:
                writer.writerow([
                    e.utilisateur_id,
                    e.livre_id,
                    e.note_utilisateur if e.note_utilisateur else 3,
                    str(e.date_emprunt),
                    e.duree_emprunt
                ])

        return Response({
            'message': f'Export réussi : {emprunts.count()} enregistrements.',
            'fichier': filepath,
            'colonnes': ['user_id', 'book_id', 'rating', 'date_emprunt', 'duree_jours'],
            'total_lignes': emprunts.count()
        })

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT 7 : Statistiques globales
    # ═══════════════════════════════════════════════════════════════
    @action(detail=False, methods=['get'], url_path='statistiques')
    def statistiques(self, request):
        """
        GET /api/emprunts/statistiques/
        Tableau de bord global des emprunts.
        """
        aujourd_hui = timezone.now().date()
        total       = Emprunt.objects.count()
        en_cours    = Emprunt.objects.filter(statut=Emprunt.Statut.EN_COURS).count()
        retournes   = Emprunt.objects.filter(statut=Emprunt.Statut.RETOURNE).count()
        en_retard   = Emprunt.objects.filter(
            statut__in=[Emprunt.Statut.EN_COURS, Emprunt.Statut.EN_RETARD],
            date_retour_prevue__lt=aujourd_hui
        ).count()

        return Response({
            'total_emprunts': total,
            'en_cours': en_cours,
            'retournes': retournes,
            'en_retard': en_retard,
            'date': str(aujourd_hui)
        })
