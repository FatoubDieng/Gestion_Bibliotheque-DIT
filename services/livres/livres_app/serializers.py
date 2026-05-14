from rest_framework import serializers
from .models import Livre


class LivreSerializer(serializers.ModelSerializer):
    disponible = serializers.ReadOnlyField()

    class Meta:
        model = Livre
        fields = '__all__'

    def validate_stock_dispo(self, value):
        if value < 0:
            raise serializers.ValidationError("Le stock disponible ne peut pas être négatif.")
        return value

    def validate(self, data):
        stock_total = data.get('stock_total', getattr(self.instance, 'stock_total', 0))
        stock_dispo = data.get('stock_dispo', getattr(self.instance, 'stock_dispo', 0))
        if stock_dispo > stock_total:
            raise serializers.ValidationError(
                "Le stock disponible ne peut pas dépasser le stock total."
            )
        return data


class LivreListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes"""
    disponible = serializers.ReadOnlyField()

    class Meta:
        model = Livre
        fields = ['id', 'titre', 'auteur', 'isbn', 'categorie',
                  'stock_dispo', 'disponible', 'couverture']