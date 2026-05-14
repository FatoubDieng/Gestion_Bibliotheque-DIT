from django.db import models


class Utilisateur(models.Model):
    """
    Modèle Utilisateur de la bibliothèque DIT.

    3 types possibles :
      - etudiant  = matricule format ETU-XXXX-XXX
      - professeur = matricule format PROF-XXX
      - personnel  = matricule format PERS-XXX
    """

    class TypeUser(models.TextChoices):
        ETUDIANT   = 'etudiant',   'Étudiant'
        PROFESSEUR = 'professeur', 'Professeur'
        PERSONNEL  = 'personnel',  'Personnel'

    nom        = models.CharField(max_length=100)
    prenom     = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    telephone  = models.CharField(max_length=20, blank=True)
    type_user  = models.CharField(
        max_length=20,
        choices=TypeUser.choices,
        default=TypeUser.ETUDIANT
    )
    matricule  = models.CharField(max_length=50, unique=True, null=True, blank=True)
    actif      = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'utilisateurs'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.type_user})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
