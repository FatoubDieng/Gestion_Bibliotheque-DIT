from rest_framework import serializers
from .models import Utilisateur


class UtilisateurSerializer(serializers.ModelSerializer):
    """Serializer complet — utilisé pour créer / modifier / détail"""
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model  = Utilisateur
        fields = '__all__'

    #  Validations 

    def validate_email(self, value):
        """L'email doit être en minuscules"""
        return value.lower().strip()

    def validate_matricule(self, value):
        """Le matricule doit respecter le format selon le type"""
        if not value:
            return value
        value = value.upper().strip()
        return value

    def validate(self, data):
        """Validation croisée : format matricule selon le type"""
        type_user = data.get('type_user', '')
        matricule = data.get('matricule', '')

        if matricule:
            prefixes = {
                'etudiant':   'ETU-',
                'professeur': 'PROF-',
                'personnel':  'PERS-',
            }
            prefix = prefixes.get(type_user, '')
            if prefix and not matricule.startswith(prefix):
                raise serializers.ValidationError({
                    'matricule': f"Le matricule d'un {type_user} doit commencer par '{prefix}'. "
                                 f"Exemple : {prefix}2024-001"
                })
        return data


class UtilisateurListSerializer(serializers.ModelSerializer):
    """Serializer léger — utilisé pour les listes"""
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model  = Utilisateur
        fields = ['id', 'nom_complet', 'email', 'type_user', 'matricule', 'actif']


class UtilisateurProfilSerializer(serializers.ModelSerializer):
    """Serializer profil — avec tous les détails sauf champs sensibles"""
    nom_complet = serializers.ReadOnlyField()

    class Meta:
        model  = Utilisateur
        fields = [
            'id', 'nom', 'prenom', 'nom_complet',
            'email', 'telephone', 'type_user',
            'matricule', 'actif', 'created_at'
        ]
        read_only_fields = ['created_at']
