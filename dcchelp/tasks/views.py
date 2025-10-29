from django.shortcuts import render
from dccpdh2.utils import DataMixin
from django.views.generic import ListView

from tasks.models import Task


class TasksView(DataMixin, ListView):
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'
    title = 'Задачи'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)

    def get_queryset(self):
        return Task.objects.all()