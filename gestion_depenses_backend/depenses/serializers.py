from rest_framework import serializers
from depenses.models import Categorie, Depense


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id", "nom", "compte", "cree_a"]
        read_only_fields = ["id", "compte", "cree_a"]


class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ["id", "compte", "utilisateur", "categorie", "monnaie", "avoir", "description", "date_depense", "cree_a"]
        read_only_fields = ["id", "compte", "utilisateur", "cree_a"]