from django.db import models


class FAQ(models.Model):
    """ Часто задаваемые вопросы """
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1000, blank=True, default='Ответа пока что нет...')

    def __str__(self):
        return self.question