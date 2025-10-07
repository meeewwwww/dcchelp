from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.generic import ListView, TemplateView

from .forms import DocumentArticleForm
from .models import Tag, Change, DocumentTypes, DocumentArticle, DocumentSubType, FAQ


menu = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'Процедуры', 'url_name': 'procedures'},
    {'title': 'Лист изменений', 'url_name': 'list_of_changes'},
    {'title': 'Оформление документации', 'url_name': 'documentation'},
    {'title': 'Запуск процессов', 'url_name': 'processes'},
    {'title': 'FAQ', 'url_name': 'FAQ'},
]


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        changes = Change.objects.all()[:4]
        articles = DocumentArticle.objects.order_by('-created').all()[:2]
        context.update({
            'menu': menu,
            'changes': changes,
            'articles': articles,
        })
        return context


class ListOfChangesView(ListView):
    template_name = 'list_of_changes.html'
    context_object_name = 'changes'
    extra_context = {'menu': menu}

    def get_queryset(self):
        return Change.objects.all()


def add_change(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            number = request.POST.get('change_number')
            title = request.POST.get('change_title')
            text = request.POST.get('change_description')  # HTML с форматированием
            link_approvement = request.POST.get('approval_link')

            if not text or text.strip() in ['', '<br>', '<p></p>', '<div><br></div>']:
                # Вернуть ошибку или обработать как считаешь нужным
                return HttpResponse("Ошибка: описание изменения обязательно", status=400)

            # Создаем изменение
            change = Change.objects.create(
                number=number,
                title=title,
                text=text,
                link_approvement=link_approvement
            )

            messages.success(request, 'Изменение успешно добавлено!')
            return redirect('list_of_changes')

        except Exception as e:
            messages.error(request, f'Ошибка при добавлении изменения: {str(e)}')

    # Для GET запроса показываем форму с тегами
    all_tags = Tag.objects.all()
    return render(request, 'list_of_changes.html', {'all_tags': all_tags})


def edit_change(request, change_id):
    change = get_object_or_404(Change, id=change_id)

    if request.method == 'POST':
        change.number = request.POST.get('change_number')
        change.title = request.POST.get('change_title')
        change.text = request.POST.get('change_description')
        change.link_approvement = request.POST.get('approval_link')
        change.save()
        return JsonResponse({'success': True})

    return JsonResponse({
        'number': change.number,
        'title': change.title,
        'text': change.text,  # отправляем как text
        'link_approvement': change.link_approvement,
    })


def cancel_change(request, change_id):
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.active = 0
        change.save()
        return JsonResponse({'success': True})


def delete_change(request, change_id):
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.delete()
        return JsonResponse({'success': True})


def documentation(request):
    document_types = DocumentTypes.objects.prefetch_related('sub_types').all()
    data = {
        'menu': menu,
        'document_types': document_types,
    }
    return render(request, 'documentation.html', context=data)


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


def add_document_article(request):
    if request.method == 'POST':
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


def get_subtypes(request, doc_type_id):
    try:
        doc_type = DocumentTypes.objects.get(id=doc_type_id)
        subtypes = doc_type.sub_types.all().values('id', 'name')
        return JsonResponse({'subtypes': list(subtypes)})
    except DocumentTypes.DoesNotExist:
        return JsonResponse({'subtypes': []})


class FAQView(ListView):
    template_name = 'faq.html'
    context_object_name = 'qas'
    extra_context = {'menu': menu}

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
def processes(request):
    data = {
        'menu': menu,
    }
    return render(request, 'base.html', context=data)


# Подумать над целесообразностью раздела
def procedures(request):
    data = {
        'menu': menu,
    }
    return render(request, 'base.html', context=data)