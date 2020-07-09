from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.postgres.fields import JSONField



class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=50, unique=True)
    meta = JSONField(default={})

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.email
