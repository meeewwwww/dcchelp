from django.contrib.auth import get_user_model
from django import forms

from tasks.models import Task


class TaskFrom(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_superuser=0).order_by('first_name'),
                                  empty_label='Не выбрано', required=False, label='Сотрудник ТДО')

    class Meta:
        model = Task
        fields = ['number', 'created', 'name', 'type', 'priority', 'iteration', 'status', 'finished', 'user', 'result', 'comment']