from datetime import timedelta
import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect
from dccpdh2.utils import DataMixin
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView

from tasks.models import Task

from tasks.forms import TaskFrom


class TasksView(DataMixin, ListView):
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'
    title = 'Задачи'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_threshold = timezone.now() - timedelta(hours=72)
        tasks = Task.objects.filter(created__gte=time_threshold)

        context['tasks'] = tasks
        context['form'] = TaskFrom()
        context['status_choices'] = Task.STATUSES
        context['iteration_choices'] = Task.ITERATIONS
        context['users'] = get_user_model().objects.all()  # ← добавить
        return self.get_mixin_context(context)

    def get_queryset(self):
        time_threshold = timezone.now() - timedelta(hours=72)
        tasks = Task.objects.filter(created__gte=time_threshold)
        return tasks


@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # для отладки
        form = TaskFrom(request.POST)
        if form.is_valid():
            task = form.save()
            print("Task saved:", task.id)  # для отладки
            return JsonResponse({'success': True})
        else:
            print("Form errors:", form.errors)  # для отладки
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def update_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            print("POST data:", dict(request.POST))  # ← что приходит

            # Обновляем все поля
            task.number = request.POST.get('number')
            task.created = request.POST.get('created')
            task.name = request.POST.get('name')
            task.priority = request.POST.get('priority') == 'true'
            task.iteration = int(request.POST.get('iteration'))
            task.status = request.POST.get('status')
            task.user_id = request.POST.get('user')
            task.result = request.POST.get('result')
            task.comment = request.POST.get('comment')

            task.save()
            print("Task saved:", task.id, task.number)  # ← подтверждение
            return JsonResponse({'success': True})
        except Exception as e:
            print("Error:", str(e))  # ← ошибки
            return JsonResponse({'success': False, 'error': str(e)})


def delete_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})