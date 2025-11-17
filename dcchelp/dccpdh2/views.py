from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from .models import FAQ
from .utils import DataMixin
from list_of_changes.models import Change
from tasks.models import Task
from documentation.models import DocumentArticle


class IndexView(DataMixin, TemplateView):
    """ Отображение главной страницы сайта """
    template_name = 'index.html'
    title = 'Главная страница'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Для дашборда со статусом задач
        tasks = Task.active_tasks.all()

        # Для дашборда с графиком задач
        chart_data = Task.active_tasks_chart_72h.all()

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
        return FAQ.objects.all()


def page_not_found(request, exception):
    """ Кастомная страница ошибки 404 """
    return render(request, '404.html', {
        'title': 'Страница не найдена',
        'menu': DataMixin.menu
    }, status=404)


def search(request):
    """ Поиск по сайту осуществляется по моделям:
    Change, поля: 'title', 'text'
    Task, поля: 'number', 'name', 'result', 'comment'
    DocumentArticle, поля: 'title', 'clean_text'"""
    query = request.GET.get('q', '')
    changes = []
    tasks = []
    articles = []

    if query:
        changes = Change.search.search(query)
        tasks = Task.search.search(query)
        articles = DocumentArticle.search.search(query)

    return render(request, 'search.html', {
        'changes': changes,
        'tasks': tasks,
        'query': query,
        'articles': articles,
        'menu': DataMixin.menu,
    })