
from datetime import timedelta, datetime
import json

from django.contrib.auth import get_user_model
from django.db.models import Q
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
        context['form'] = TaskFrom()
        context['status_choices'] = Task.STATUSES
        context['iteration_choices'] = Task.ITERATIONS
        context['users'] = get_user_model().objects.filter(is_superuser=0).order_by('first_name')
        return self.get_mixin_context(context)

    def get_queryset(self):
        time_threshold = timezone.now() - timedelta(hours=72)
        tasks = Task.objects.filter(
            Q(created__gte=time_threshold) |
            Q(status__in=['not_taken', 'in_progress', 'on_hold'])
        ).order_by('-created')
        return tasks


@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        form = TaskFrom(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            task.number = request.POST.get('number')
            created_str = request.POST.get('created')

            try:
                created_dt = datetime.strptime(created_str, '%d.%m.%Y %H:%M')
                task.created = created_dt
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': f'Неверный формат даты: {created_str}. Используйте ДД.ММ.ГГГГ ЧЧ:ММ'
                })

            task.name = request.POST.get('name')
            task.priority = request.POST.get('priority') == 'true'
            task.iteration = int(request.POST.get('iteration'))
            task.status = request.POST.get('status')

            # Правильная обработка поля finished
            finished_str = request.POST.get('finished')
            if finished_str:
                try:
                    task.finished = finished_str  # 'YYYY-MM-DD' формат уже правильный
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': f'Неверный формат даты завершения: {finished_str}'
                    })
            else:
                task.finished = None  # Устанавливаем None если поле пустое

            task.user_id = request.POST.get('user')
            task.result = request.POST.get('result')
            task.comment = request.POST.get('comment')

            print("Received data:", dict(request.POST))
            task.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


def delete_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})