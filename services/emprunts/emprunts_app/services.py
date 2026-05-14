"""
DIT Bibliothèque — Service Emprunts
Client HTTP pour communiquer avec les autres services

Ce module gère toute la communication inter-services :
  - Vérifier qu'un livre existe et est disponible  → Service Livres
  - Vérifier qu'un utilisateur existe et est actif → Service Users
  - Notifier le stock lors d'un emprunt/retour      → Service Livres
"""
import requests
from django.conf import settings


class ServiceLivresClient:
    """
    Client pour le Service Livres (port 8001).
    Toutes les appels HTTP vers service-livres passent par ici.
    """

    def __init__(self):
        self.base_url = settings.SERVICE_LIVRES_URL

    def get_livre(self, livre_id: int) -> dict | None:
        """
        Récupère les infos d'un livre par son ID.
        Retourne None si le livre n'existe pas.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/livres/{livre_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None

    def verifier_disponibilite(self, livre_id: int) -> tuple[bool, str]:
        """
        Vérifie si un livre est disponible pour l'emprunt.
        Retourne (True, '') si disponible, (False, message) sinon.
        """
        livre = self.get_livre(livre_id)

        if livre is None:
            return False, f"Livre avec l'ID {livre_id} introuvable."

        if livre.get('stock_dispo', 0) <= 0:
            return False, f"Le livre '{livre.get('titre')}' n'est plus disponible (stock épuisé)."

        return True, ''

    def decrementer_stock(self, livre_id: int) -> bool:
        """
        Notifie le service Livres de décrémenter le stock.
        Appelé lors d'un emprunt.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/livres/{livre_id}/emprunter/",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def incrementer_stock(self, livre_id: int) -> bool:
        """
        Notifie le service Livres d'incrémenter le stock.
        Appelé lors du retour d'un livre.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/livres/{livre_id}/retourner/",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class ServiceUsersClient:
    """
    Client pour le Service Utilisateurs (port 8002).
    Toutes les appels HTTP vers service-users passent par ici.
    """

    def __init__(self):
        self.base_url = settings.SERVICE_USERS_URL

    def get_utilisateur(self, utilisateur_id: int) -> dict | None:
        """
        Récupère les infos d'un utilisateur par son ID.
        Retourne None si l'utilisateur n'existe pas.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/users/{utilisateur_id}/",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None

    def verifier_utilisateur(self, utilisateur_id: int) -> tuple[bool, str]:
        """
        Vérifie qu'un utilisateur existe et est actif.
        Retourne (True, '') si valide, (False, message) sinon.
        """
        utilisateur = self.get_utilisateur(utilisateur_id)

        if utilisateur is None:
            return False, f"Utilisateur avec l'ID {utilisateur_id} introuvable."

        if not utilisateur.get('actif', False):
            return False, f"Le compte de {utilisateur.get('nom_complet', '')} est désactivé."

        return True, ''
