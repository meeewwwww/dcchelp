from django.contrib.auth.models import User
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1000, blank=True, default='Ответа пока что нет...')
    answered = models.BooleanField(default=False)