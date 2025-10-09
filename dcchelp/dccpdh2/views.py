from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, DeleteView

from .forms import DocumentArticleForm, ChangeForm
from .models import Tag, Change, DocumentTypes, DocumentArticle, DocumentSubType, FAQ
from .utils import DataMixin


# Главная страница. +Дополнить еще двумя разделами для отображения
class IndexView(DataMixin, TemplateView):
    template_name = 'index.html'
    title = 'Главная страница'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
                                      changes=Change.objects.all()[:4],
                                      articles=DocumentArticle.objects.order_by('-created').all()[:4])


# Раздел листа изменений
class ListOfChangesView(DataMixin, ListView):
    template_name = 'list_of_changes.html'
    context_object_name = 'changes'
    title = 'Лист изменений'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)

    def get_queryset(self):
        return Change.objects.all()


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def add_change(request):
    if request.method == 'POST':
        form = ChangeForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def edit_change(request, change_id):
    change = get_object_or_404(Change, id=change_id)
    if request.method == 'POST':
        form = ChangeForm(request.POST, instance=change)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({
        'number': change.number,
        'title': change.title,
        'text': change.text,
        'link_approvement': change.link_approvement,
    })


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def cancel_change(request, change_id):
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.active = 0
        change.save()
        return JsonResponse({'success': True})


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
def delete_change(request, change_id):
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.delete()
        return JsonResponse({'success': True})


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
        content = render_to_string('articles_list.html', {'articles': articles})

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


# Подумать над целесообразностью раздела
class ProcessesView(DataMixin, TemplateView):
    template_name = 'base.html'
    title = 'Запуск процессов'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)


# Подумать над целесообразностью раздела
class ProceduresView(DataMixin, TemplateView):
    template_name = 'base.html'
    title = 'Процедуры'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)