from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import HttpResponse
from comptes.services import obtenir_compte_utilisateur, obtenir_role_utilisateur
from depenses.models import Categorie
from depenses.serializers import CategorieSerializer, DepenseSerializer
from depenses.services import (
    valider_donnee_depense,
    construire_requete_depense,
    depense_totale_par_categorie,
    depense_totale_par_devise,
    depense_totale_par_utilisateur,
    periode_depense,
    exporter_rapport
)

class CategorieViewSet(viewsets.ModelViewSet):
    serializer_class = CategorieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def obtenir_requete(self):
        compte = obtenir_compte_utilisateur(self.request.user)
        return Categorie.objects.filter(compte=compte)
    
    def executer_creation(self, serializer):
        compte = obtenir_compte_utilisateur(self.request.user)
        role = obtenir_role_utilisateur(self.request.user, compte)

        if role == "INVITER":
            raise PermissionDenied("Un invité ne peut créer des catégories")
        serializer.save(compte=compte)


class DepenseViewSet(viewsets.ModelViewSet):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def obtenir_requete(self):
        return construire_requete_depense(self.request.user, self.request.query_params)
    
    def executer_creation(self, serializer):
        compte = obtenir_compte_utilisateur(self.request.user)
        role = obtenir_role_utilisateur(self.request.user, compte)
        valider_donnee_depense(serializer.validated_data, compte, self.request.user, role)
        serializer.save(compte=compte, utilisateur=self.request.user)

    
class RapportDepenseParCategorie(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        requete_depense = construire_requete_depense(requete.user, requete.query_params)
        donnee = depense_totale_par_categorie(requete_depense)
        return Response(donnee)


class RapportDepenseParUtilisateur(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        compte = obtenir_compte_utilisateur(requete.user)
        role = obtenir_role_utilisateur(requete.user, compte)
        requete_depense = construire_requete_depense(requete.user, requete.query_params)
        donnee = depense_totale_par_utilisateur(requete_depense, requete.user, role)
        return Response(donnee)
    

class RapportDepenseParPeriode(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        periode = requete.query_params.get("periode", "mois")
        requete_depense = construire_requete_depense(requete.user, requete.query_params)
        donnee = periode_depense(requete_depense, periode)
        return Response(donnee)
    

class RapportDepenseParMonnaie(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        requete_depense = construire_requete_depense(requete.user, requete.query_params)
        donnee = depense_totale_par_devise(requete_depense)
        return Response(donnee)
    

class RapportDepenseExporter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requete):
        requete_depense = construire_requete_depense(requete.user, requete.query_params)
        fichier = exporter_rapport(requete_depense, type_rapport="csv")
        reponse = HttpResponse(fichier, content_type="text/csv")
        reponse["Content-Disposition"] = "attachment; filename='rapport_depenses.csv'"
        return reponse