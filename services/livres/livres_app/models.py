from django.db import models


class Livre(models.Model):
    titre       = models.CharField(max_length=255)
    auteur      = models.CharField(max_length=255)
    isbn        = models.CharField(max_length=20, unique=True)
    categorie   = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    annee       = models.IntegerField(null=True, blank=True)
    editeur     = models.CharField(max_length=150, blank=True)
    stock_total = models.IntegerField(default=1)
    stock_dispo = models.IntegerField(default=1)
    couverture  = models.URLField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'livres'
        ordering = ['titre']

    def __str__(self):
        return f"{self.titre} — {self.auteur}"

    @property
    def disponible(self):
        return self.stock_dispo > 0