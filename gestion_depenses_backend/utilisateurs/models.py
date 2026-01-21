from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    cree_a = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email