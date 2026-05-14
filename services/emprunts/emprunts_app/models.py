from django.db import models
from django.utils import timezone


class Emprunt(models.Model):
    """
    Modèle Emprunt — cœur du système bibliothèque.

    Cycle de vie d'un emprunt :
      1. Créé        → statut = 'en_cours'
      2. Retardé     → statut = 'en_retard'  (date_retour_prevue dépassée)
      3. Retourné    → statut = 'retourne'   (date_retour_reel renseignée)

    Champs importants pour le ML :
      - utilisateur_id  → qui a emprunté
      - livre_id        → quel livre
      - note_utilisateur → note donnée au livre (1-5) → utilisée comme score
    """

    class Statut(models.TextChoices):
        EN_COURS  = 'en_cours',  'En cours'
        RETOURNE  = 'retourne',  'Retourné'
        EN_RETARD = 'en_retard', 'En retard'

    # ── Clés étrangères (IDs des autres services) ────────────────
    # On ne fait pas de FK vers d'autres services
    # On stocke juste les IDs → chaque service est indépendant
    utilisateur_id     = models.IntegerField()
    livre_id           = models.IntegerField()

    # ── Dates ────────────────────────────────────────────────────
    date_emprunt       = models.DateField(default=timezone.now)
    date_retour_prevue = models.DateField()
    date_retour_reel   = models.DateField(null=True, blank=True)

    # ── Statut ───────────────────────────────────────────────────
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_COURS
    )

    # ── Avis de l'utilisateur (utile pour le ML) ─────────────────
    note_utilisateur = models.IntegerField(
        null=True, blank=True,
        choices=[(i, str(i)) for i in range(1, 6)]  # 1 à 5 étoiles
    )
    commentaire = models.TextField(blank=True)

    # ── Timestamps ───────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'emprunts'
        ordering = ['-date_emprunt']

    def __str__(self):
        return f"Emprunt #{self.id} — User {self.utilisateur_id} / Livre {self.livre_id}"

    @property
    def est_en_retard(self):
        """Retourne True si la date de retour prévue est dépassée"""
        if self.statut == self.Statut.RETOURNE:
            return False
        return timezone.now().date() > self.date_retour_prevue

    @property
    def jours_retard(self):
        """Nombre de jours de retard (0 si pas en retard)"""
        if not self.est_en_retard:
            return 0
        return (timezone.now().date() - self.date_retour_prevue).days

    @property
    def duree_emprunt(self):
        """Durée totale de l'emprunt en jours"""
        fin = self.date_retour_reel or timezone.now().date()
        return (fin - self.date_emprunt).days
