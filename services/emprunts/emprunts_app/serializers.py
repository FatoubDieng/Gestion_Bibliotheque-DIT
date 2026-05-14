from rest_framework import serializers
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Emprunt


class EmpruntSerializer(serializers.ModelSerializer):
    """Serializer complet"""
    est_en_retard  = serializers.ReadOnlyField()
    jours_retard   = serializers.ReadOnlyField()
    duree_emprunt  = serializers.ReadOnlyField()

    class Meta:
        model  = Emprunt
        fields = '__all__'
        read_only_fields = [
            'statut', 'date_retour_reel',
            'created_at', 'updated_at'
        ]

    def validate_note_utilisateur(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


class EmpruntCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer un emprunt.
    Seuls utilisateur_id et livre_id sont requis.
    La date_retour_prevue est calculée automatiquement.
    """

    class Meta:
        model  = Emprunt
        fields = ['utilisateur_id', 'livre_id', 'note_utilisateur', 'commentaire']

    def create(self, validated_data):
        max_days = settings.MAX_BORROW_DAYS
        validated_data['date_emprunt']       = timezone.now().date()
        validated_data['date_retour_prevue'] = timezone.now().date() + timedelta(days=max_days)
        validated_data['statut']             = Emprunt.Statut.EN_COURS
        return super().create(validated_data)


class EmpruntListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes"""
    est_en_retard = serializers.ReadOnlyField()
    jours_retard  = serializers.ReadOnlyField()

    class Meta:
        model  = Emprunt
        fields = [
            'id', 'utilisateur_id', 'livre_id',
            'date_emprunt', 'date_retour_prevue',
            'date_retour_reel', 'statut',
            'est_en_retard', 'jours_retard'
        ]


class RetourSerializer(serializers.Serializer):
    """Serializer pour le retour d'un livre"""
    note_utilisateur = serializers.IntegerField(min_value=1, max_value=5, required=False)
    commentaire      = serializers.CharField(required=False, allow_blank=True)
