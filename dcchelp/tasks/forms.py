from django.forms import ModelForm

from tasks.models import Task


class TaskFrom(ModelForm):

    class Meta:
        model = Task
        fields = ['number', 'created', 'name', 'priority', 'iteration', 'status', 'finished', 'user', 'result', 'comment']