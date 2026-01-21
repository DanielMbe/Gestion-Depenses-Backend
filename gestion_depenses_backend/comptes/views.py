from rest_framework import viewsets, permissions
from comptes.models import Compte, RoleUtilisateur
from comptes.serializers import CompteSerializer


class CompteViewSet(viewsets.ModelViewSet):
    serializer_class = CompteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def obtenir_requete(self):
        return Compte.objects.filter(nom=self.request.user)
    
    def executer_creation(self, serializer):
        compte = serializer.save()
        RoleUtilisateur.objects.create(utilisateur=self.request.user, compte=compte, role=RoleUtilisateur.PROPRIETAIRE)