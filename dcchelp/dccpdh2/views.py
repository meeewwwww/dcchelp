from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView, CreateView, DeleteView

from .forms import DocumentArticleForm, DocumentArticleEditForm
from .models import DocumentTypes, DocumentArticle, DocumentSubType, FAQ
from .utils import DataMixin
from list_of_changes.models import Change

from tasks.models import Task


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
                                      changes=Change.objects.all()[:4],

                                      articles=DocumentArticle.objects.order_by('-created').all()[:4],

                                      active_tasks=tasks.count(),
                                      in_progress=tasks.filter(status='in_progress').count(),
                                      not_taken=tasks.filter(status='not_taken').count(),
                                      high_priority=tasks.filter(priority=1).count(),
                                      on_hold=tasks.filter(status='on_hold').count(),

                                      chart_data=chart_data
                                      )


class DocumentationView(DataMixin, TemplateView):
    template_name = 'documentation.html'
    title = 'Оформление документации'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
                                      document_types=DocumentTypes.objects.prefetch_related('sub_types').all())


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def get_documentation_content(request, doc_type_id, subtype_id=None):
    if subtype_id:
        articles = DocumentArticle.objects.filter(
            doc_type_id=doc_type_id,
            doc_sub_type_id=subtype_id
        ).order_by('-created')
        subtype = DocumentSubType.objects.get(id=subtype_id)
        doc_type = DocumentTypes.objects.get(id=doc_type_id)

        content = render_to_string('articles_list.html', {
            'articles': articles,
            'doc_type_name': doc_type.ru_name,
            'subtype_name': subtype.name
        })

        return JsonResponse({
            'title': f'{subtype.name}',
            'content': content
        })

    else:
        doc_type = get_object_or_404(DocumentTypes, id=doc_type_id)
        articles = DocumentArticle.objects.filter(doc_type_id=doc_type_id)
        content = render_to_string('articles_list.html', {'articles': articles})

        return JsonResponse({
            'title': doc_type.ru_name,
            'content': content
        })


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def add_document_article(request):
    if request.method == 'POST':
        print("POST данные:", request.POST)  # ← что приходит
        form = DocumentArticleForm(request.POST)
        if 'doc_type' in request.POST:
            try:
                doc_type_id = int(request.POST['doc_type'])
                form.fields['doc_sub_type'].queryset = DocumentSubType.objects.filter(doc_types__id=doc_type_id)
            except (ValueError, TypeError):
                pass

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = DocumentArticleForm()
        content = render(request, 'add_document_article.html', {'form': form})
        return JsonResponse({
            'content': content.content.decode('utf-8'),
            'title': 'Добавить статью'
        })


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def get_subtypes(request, doc_type_id):
    try:
        doc_type = DocumentTypes.objects.get(id=doc_type_id)
        subtypes = doc_type.sub_types.all().values('id', 'name')
        return JsonResponse({'subtypes': list(subtypes)})
    except DocumentTypes.DoesNotExist:
        return JsonResponse({'subtypes': []})


def edit_article(request, article_id):
    article = get_object_or_404(DocumentArticle, id=article_id)
    if request.method == 'POST':
        form = DocumentArticleEditForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({
        'title': article.title,
        'text': article.text,
    })


def delete_article(request, article_id):
    if request.method == 'POST':
        article = get_object_or_404(DocumentArticle, id=article_id)
        article.delete()
        return JsonResponse({'success': True})


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