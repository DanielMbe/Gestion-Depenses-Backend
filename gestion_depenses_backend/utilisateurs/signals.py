from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from comptes.models import Compte, RoleUtilisateur


Utilisateur = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_nouveau_compte(sender, instance, cree_a, **kwargs):
    if cree_a:
        compte = Compte.objects.create(nom=f"Compte de {instance.email}", proprietaire=instance)
        RoleUtilisateur.objects.create(utilisateur=instance, compte=compte, role=RoleUtilisateur.PROPRIETAIRE)