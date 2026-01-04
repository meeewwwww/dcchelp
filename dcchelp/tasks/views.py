from datetime import timedelta, datetime

import pandas as pd
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from dccpdh2.utils import DataMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

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
        context['types_choices'] = Task.TYPES_OF_TASK
        context['users'] = get_user_model().objects.filter(is_superuser=0).order_by('first_name')
        return self.get_mixin_context(context)

    def get_queryset(self):
        time_threshold = timezone.now() - timedelta(hours=7200) # ИЗМЕНИТЬ НА 72 НА ПРОДЕ, 7200 ДЛЯ ТЕСТА
        tasks = Task.objects.filter(
            Q(created__gte=time_threshold) |
            Q(status__in=['not_taken', 'in_progress', 'on_hold'])
        )
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

            task.type = request.POST.get('type')
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


def archive_statistics(request):
    users = get_user_model().objects.filter(is_superuser=False).order_by('first_name')

    context = {
        'users': users,
        'menu': DataMixin.menu,
    }
    return render(request, 'tasks/archive_statistics.html', context)


def get_statistics_data(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        user_id = request.GET.get('user')

        tasks = Task.objects.all()

        # Фильтрация по дате
        if start_date:
            try:
                start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
                tasks = tasks.filter(created__gte=start_date_dt)
            except ValueError:
                return JsonResponse({'error': 'Неверный формат начальной даты'})

        if end_date:
            try:
                end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
                # Добавляем время для включения всего дня
                end_date_dt = end_date_dt.replace(hour=23, minute=59, second=59)
                tasks = tasks.filter(created__lte=end_date_dt)
            except ValueError:
                return JsonResponse({'error': 'Неверный формат конечной даты'})

        if user_id:
            # Статистика для конкретного пользователя
            try:
                tasks = tasks.filter(user_id=int(user_id))
                user_stats = tasks.extra(
                    {'date_created': "date(created)"}
                ).values('date_created').annotate(
                    count=Count('id')
                ).order_by('date_created')

                if user_stats:
                    data = {
                        'labels': [item['date_created'] for item in user_stats],
                        'data': [item['count'] for item in user_stats],
                        'type': 'user'
                    }
                else:
                    # Если задач нет, возвращаем пустые данные с сообщением
                    data = {
                        'labels': [],
                        'data': [],
                        'type': 'user',
                        'message': 'Нет данных за выбранный период'
                    }

            except ValueError:
                return JsonResponse({'error': 'Неверный ID пользователя'})
        else:
            # Статистика по всем пользователям
            user_stats = tasks.values(
                'user__first_name', 'user__last_name', 'user__username', 'user_id'
            ).annotate(
                count=Count('id')
            ).order_by('-count')

            labels = []
            counts = []

            for item in user_stats:
                if item['user_id']:
                    # Формируем имя пользователя
                    full_name = f"{item['user__first_name'] or ''} {item['user__last_name'] or ''}".strip()
                    if full_name:
                        labels.append(full_name)
                    else:
                        labels.append(item['user__username'] or f"User #{item['user_id']}")
                else:
                    # Если пользователь не указан
                    labels.append("Не выбрано")

                counts.append(item['count'])

            data = {
                'labels': labels,
                'data': counts,
                'type': 'users'
            }

            # Если нет данных, добавляем сообщение
            if not any(counts):
                data['message'] = 'Нет данных за выбранный период'

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method'})


def export_to_excel(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        tasks = Task.objects.all()

        # Фильтрация по дате
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            tasks = tasks.filter(created__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            tasks = tasks.filter(created__lte=end_date)

        # Создание DataFrame
        data = []
        for task in tasks:
            data.append({
                'Number': task.number,
                'Created': task.created.strftime('%d.%m.%Y %H:%M') if task.created else '',
                'Name': task.name,
                'Type': task.type,
                'Priority': 'Да' if task.priority else 'Нет',
                'Iteration': task.iteration,
                'Status': task.status,
                'Finished': task.finished.strftime('%d.%m.%Y') if task.finished else '',
                'User': f"{task.user.first_name} {task.user.last_name}" if task.user else '',
                'Result': task.result,
                'Comment': task.comment
            })

        df = pd.DataFrame(data)

        # Создание HTTP ответа с Excel файлом
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="archive_data.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Archive Data', index=False)

            # Автонастройка ширины колонок
            worksheet = writer.sheets['Archive Data']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        return response

    return JsonResponse({'error': 'Invalid request method'})


def search_tasks(request):
    if request.method == 'GET':
        number = request.GET.get('number')
        name = request.GET.get('name')

        tasks = Task.objects.all()

        if number:
            tasks = tasks.filter(number__icontains=number)
        if name:
            tasks = tasks.filter(name__icontains=name)

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'number': task.number,
                'created': task.created.strftime('%d.%m.%Y %H:%M') if task.created else '',
                'name': task.name,
                'type': task.type,
                'priority': task.priority,
                'iteration': task.iteration,
                'status': task.status,
                'finished': task.finished.strftime('%Y-%m-%d') if task.finished else '',
                'user_id': task.user_id,
                'user_name': f"{task.user.first_name} {task.user.last_name}" if task.user else '',
                'result': task.result,
                'comment': task.comment
            })

        return JsonResponse({'tasks': tasks_data})

    return JsonResponse({'error': 'Invalid request method'})