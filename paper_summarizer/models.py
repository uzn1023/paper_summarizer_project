from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField('メールアドレス', unique=True)
    GeminiAPI = models.CharField(max_length=255, blank=True, null=True)
    OpenaiAPI = models.CharField(max_length=255, blank=True, null=True)
    NotionAPI = models.CharField(max_length=255, blank=True, null=True)
    NotionDatabaseID = models.CharField(max_length=255, blank=True, null=True)
