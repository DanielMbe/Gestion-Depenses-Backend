from django.db import models
from comptes.models import Compte
from django.conf import settings


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name="categories")
    cree_a = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("nom", "compte")

    def __str__(self):
        return f"{self.nom} ({self.compte})"
    

class Monnaie(models.Model):
    code = models.CharField(max_length=3, unique=True)
    nom = models.CharField(max_length=50)
    symbole = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code}"
    

Utilisateur = settings.AUTH_USER_MODEL

class Depense(models.Model):
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name="depenses")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name="depenses")
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="depenses")
    monnaie = models.ForeignKey(Monnaie, on_delete=models.PROTECT, related_name="depenses")
    avoir = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(max_length=512, blank=True)
    date_depense = models.DateField()
    cree_a = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_depense", "-cree_a"]
        indexes = [models.Index(fields=["compte"]), models.Index(fields=["date_depense"])]

    def __str__(self):
        return f"{self.avoir} {self.monnaie} - {self.categorie}"