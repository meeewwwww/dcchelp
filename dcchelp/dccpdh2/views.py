from collections import defaultdict
from datetime import timedelta

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from .models import FAQ
from .utils import DataMixin
from list_of_changes.models import Change
from tasks.models import Task
from documentation.models import DocumentArticle


# Главная страница.
class IndexView(DataMixin, TemplateView):
    template_name = 'index.html'
    title = 'Главная страница'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для дашборда со статусом задач
        tasks = Task.objects.filter(status__in=['not_taken', 'in_progress', 'on_hold'])

        # Для дашборда с графиком задач
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        all_tasks = Task.objects.all()

        # Группируем задачи по дате создания
        tasks_by_date = defaultdict(int)
        for task in all_tasks:
            date_created = task.created.date()
            if date_created >= start_date:
                tasks_by_date[date_created] += 1

        # Заполняем все даты за последние 30 дней
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            chart_data.append({
                'date': current_date.strftime('%d.%m'),
                'count': tasks_by_date.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        return self.get_mixin_context(context,
                                      changes=Change.objects.all()[:6],

                                      articles=DocumentArticle.objects.order_by('-updated').all()[:4],

                                      active_tasks=tasks.count(),
                                      in_progress=tasks.filter(status='in_progress').count(),
                                      not_taken=tasks.filter(status='not_taken').count(),
                                      high_priority=tasks.filter(priority=1).count(),
                                      on_hold=tasks.filter(status='on_hold').count(),

                                      chart_data=chart_data
                                      )


class FAQView(DataMixin, ListView):
    template_name = 'faq.html'
    context_object_name = 'qas'
    title = 'FAQ'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)

    def get_queryset(self):
        return FAQ.objects.filter(answered=True)


# Разобраться и реализовать поиск по сайту
def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = YourModel.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    return render(request, 'search_results.html', {
        'results': results,
        'query': query
    })


# Разработать какую-то крутецкую 404
def page_not_found(request, exception):
    text = '''Woops! Страница не найдена.'''
    return HttpResponseServerError(text)