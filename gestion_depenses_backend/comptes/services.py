from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from comptes.models import RoleUtilisateur


def obtenir_compte_utilisateur(utilisateur):
    if not utilisateur or not utilisateur.is_authenticated:
        raise NotAuthenticated("Authentification requis")
    
    try:
        role_utilisateur = RoleUtilisateur.objects.select_related("compte").get(utilisateur=utilisateur)
    except RoleUtilisateur.DoesNotExist:
        raise PermissionDenied("Cet utilisateur n'a pas de compte")
    
    if not utilisateur.is_active:
        raise PermissionDenied("Utilisateur inactif")
    
    return role_utilisateur.compte


def obtenir_role_utilisateur(utilisateur, compte):
    try:
        role_utilisateur = RoleUtilisateur.objects.get(utilisateur=utilisateur, compte=compte)
    except RoleUtilisateur.DoesNotExist:
        raise PermissionDenied("Aucun role trouvé pour ce compte")
    
    return role_utilisateur.role