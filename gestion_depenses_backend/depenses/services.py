from depenses.models import Depense, Monnaie
from comptes.models import RoleUtilisateur
from comptes.services import (obtenir_compte_utilisateur, obtenir_role_utilisateur)
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from rest_framework.exceptions import PermissionDenied
from collections import OrderedDict
from io import StringIO
import csv


def peut_gerer_categories(role):
    return role == RoleUtilisateur.PROPRIETAIRE


def peut_voir_depense(utilisateur, role, depense):
    if depense.compte.nom != utilisateur.email:
        return False
    
    if role == RoleUtilisateur.PROPRIETAIRE:
        return True
    
    return depense.utilisateur.email == utilisateur.email


def peut_modifier_depense(utilisateur, role, depense):
    if role == RoleUtilisateur.PROPRIETAIRE:
        return True
    
    return depense.utilisateur.email == utilisateur.email


def filtrer_depense(requetes, params_requete, role):
    categorie = params_requete.get("categorie")
    date_debut = params_requete.get("date_debut")
    date_fin = params_requete.get("date_fin")
    monnaie = params_requete.get("monnaie")
    utilisateur = params_requete.get("utilisateur")

    if categorie:
        requetes = requetes.filter(categorie_id=categorie)

    if monnaie:
        requetes = requetes.filter(monnaie_id=monnaie)

    if date_debut:
        requetes = requetes.filter(expense_date__date__gte=date_debut)

    if date_fin:
        requetes = requetes.filter(expense_date__date__lte=date_fin)

    if utilisateur and role == RoleUtilisateur.OWNER:
        requetes = requetes.filter(utilisateur_id=utilisateur)

    return requetes


def restreindre_par_role(requetes, utilisateur, role):
    if role == RoleUtilisateur.PROPRIETAIRE:
        return requetes
    return requetes.filter(utilisateur=utilisateur)


def valider_appartenance_categorie(categorie, compte):
    if categorie.compte.nom != compte.nom:
        raise ValidationError("Cette categorie n'appartient à aucun compte")
    

def valider_donnee_depense(donnee, compte, utilisateur, role):
    avoir = donnee.get("avoir")
    categorie = donnee.get("category")
    monnaie = donnee.get("monnaie")
    utilisateur_depense = donnee.get("utilisateur", utilisateur)

    if avoir is None or avoir <= 0:
        raise ValidationError("L'avoir doit être supérieur à zero")
    
    if categorie.compte.nom != compte.nom:
        raise ValidationError("Catégorie invalide pour ce compte")
    
    if monnaie and not Monnaie.objects.filter(id=monnaie.id).exists():
        raise ValidationError("Devise invalide")
    
    if role == RoleUtilisateur.INVITER and utilisateur_depense != utilisateur:
        raise PermissionDenied("Un inviter ne peut créer une dépense pour d'autres utilisateurs")
    

def construire_requete_depense(utilisateur, params_requete):
    compte = obtenir_compte_utilisateur(utilisateur)
    role = obtenir_role_utilisateur(utilisateur, compte)

    requete = (Depense.objects.select_related("categorie", "monnaie", "utilisateur", "compte").filter(compte=compte))
    requete = restreindre_par_role(requete, utilisateur, role)
    requete = filtrer_depense(requete, params_requete, role)

    return requete


def depense_totale_par_categorie(requete):
    donnee = (requete.values("categorie__name").annotate(total=Sum("avoir")).order_by("-total"))
    return [{"categorie": d["categorie__name"], "total": d["total"]} for d in donnee]


def depense_totale_par_utilisateur(requete, utilisateur, role):
    if role == RoleUtilisateur.INVITER:
        total = requete.filter(utilisateur=utilisateur).aggregate(total=Sum("avoir"))["total"] or 0
        return [{"utilisateur": utilisateur.username, "total": total}]
    
    donnee = (requete.values("utilisateur__username").annotate(total=Sum("avoir")).order_by("-total"))
    return [{"utilisateur": d["utilisateur__username"], "total": d["total"]} for d in donnee]


def periode_depense(requete, periode="mois"):
    if periode == "jour":
        trunc_func = TruncDay
    elif periode == "semaine":
        trunc_func = TruncWeek
    else:
        trunc_func = TruncMonth

    donnee = (requete.annotate(periode=trunc_func("date_depense")).values("periode").annotate(totale=Sum("avoir")).order_by("periode"))
    resultat = OrderedDict()

    for d in donnee:
        resultat[d["periode"].strftime("%Y-%m-%d")] = d["total"]
    return resultat


def depense_totale_par_devise(requete):
    donnee = (requete.values("monnaie__code").annotate(total=Sum("avoir")).order_by("-total"))
    return [{"monnaie": d["monnaie__code"], "total": d["total"]} for d in donnee]


def exporter_rapport(requete, type_rapport="csv"):
    if type_rapport != "csv":
        raise ValidationError("Seulement le format CSV est disponible pour le moment")
    
    sortie = StringIO()
    ecriture = csv.writer(sortie)
    ecriture.writerow(["Utilisateur", "Categorie", "Avoir", "Monnaie", "Date", "Description"])

    for depense in requete.select_related("utilisateur", "categorie", "monnaie").all():
        ecriture.writerow([
            depense.utilisateur.username,
            depense.categorie.nom,
            depense.avoir,
            depense.monnaie.code,
            depense.date_depense.strftime('%Y-%m-%d'),
            depense.description
        ])

    sortie.seek(0)
    return sortie