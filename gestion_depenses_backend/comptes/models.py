from django.db import models
from django.conf import settings


Utilisateur = settings.AUTH_USER_MODEL

class Compte(models.Model):
    nom = models.CharField(max_length=255)
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="compte_proprietaire")
    cree_a = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
    

class RoleUtilisateur(models.Model):
    PROPRIETAIRE = "PROPRIETAIRE"
    INVITER = "INVITER"
    CHOIX_ROLE = ((PROPRIETAIRE, "PROPRIETAIRE"), (INVITER, "INVITER"))

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="role")
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name="inviter")
    role = models.CharField(max_length=12, choices=CHOIX_ROLE)
    cree_a = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("utilisateur", "compte")

    def __str__(self):
        return f"{self.utilisateur} - {self.role}"