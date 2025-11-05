from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from dccpdh2.utils import DataMixin
from documentation.models import DocumentTypes, DocumentArticle, DocumentSubType
from documentation.forms import DocumentArticleForm, DocumentArticleEditForm, DocumentTypesEditForm, DocumentSubTypeEditForm


class DocumentationView(DataMixin, TemplateView):
    template_name = 'documentation/documentation.html'
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

        content = render_to_string('documentation/articles_list.html', {
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
        content = render_to_string('documentation/articles_list.html', {'articles': articles})

        return JsonResponse({
            'title': doc_type.ru_name,
            'content': content
        })


# Реализована функция, т.к. используется AJAX (обновление данных на странице без обновления самой страницы)
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
        content = render(request, 'documentation/add_document_article.html', {'form': form})
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


def edit_types(request):
    if request.method == 'POST':
        # Проверяем, была ли отправлена форма типа
        if 'type' in request.POST:
            type_data = {
                'ru_name': request.POST.get('ru_name'),
                'en_name': request.POST.get('en_name'),
                'ru_short': request.POST.get('ru_short'),
                'en_short': request.POST.get('en_short'),
                'sub_types': request.POST.getlist('sub_types')  # Для ManyToMany field
            }
            form = DocumentTypesEditForm(type_data)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        # Проверяем, была ли отправлена форма подтипа
        elif 'subtype' in request.POST:
            subtype_data = {
                'name': request.POST.get('name')
            }
            form = DocumentSubTypeEditForm(subtype_data)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors})

        # Обработка добавления связи
        elif 'add_relation' in request.POST:
            type_id = request.POST.get('type_id')
            subtype_id = request.POST.get('subtype_id')

            try:
                doc_type = DocumentTypes.objects.get(id=type_id)
                subtype = DocumentSubType.objects.get(id=subtype_id)

                # Добавляем связь
                doc_type.sub_types.add(subtype)
                return JsonResponse({'success': True})

            except (DocumentTypes.DoesNotExist, DocumentSubType.DoesNotExist):
                return JsonResponse({'success': False, 'errors': 'Тип или подтип не найден'})

            # Обработка удаления связи
        elif 'delete_relation' in request.POST:
            type_id = request.POST.get('type_id')
            subtype_id = request.POST.get('subtype_id')

            try:
                doc_type = DocumentTypes.objects.get(id=type_id)
                subtype = DocumentSubType.objects.get(id=subtype_id)

                # Удаляем связь
                doc_type.sub_types.remove(subtype)
                return JsonResponse({'success': True})

            except (DocumentTypes.DoesNotExist, DocumentSubType.DoesNotExist):
                return JsonResponse({'success': False, 'errors': 'Тип или подтип не найден'})

        # Обработка удаления типа
        elif 'delete_type' in request.POST:
            type_id = request.POST.get('type_id')
            try:
                doc_type = DocumentTypes.objects.get(id=type_id)
                doc_type.delete()
                return JsonResponse({'success': True})
            except DocumentTypes.DoesNotExist:
                return JsonResponse({'success': False, 'errors': 'Тип не найден'})

            # Обработка удаления подтипа
        elif 'delete_subtype' in request.POST:
            subtype_id = request.POST.get('subtype_id')
            try:
                subtype = DocumentSubType.objects.get(id=subtype_id)
                subtype.delete()
                return JsonResponse({'success': True})
            except DocumentSubType.DoesNotExist:
                return JsonResponse({'success': False, 'errors': 'Подтип не найден'})

    else:
        form_type = DocumentTypesEditForm()
        form_sub_type = DocumentSubTypeEditForm()
        return render(request, 'documentation/edit_types.html', {
            'menu': DataMixin.menu,
            'form_type': form_type,
            'form_sub_type': form_sub_type,
            'title': 'Редактировать типы / подтипы'
        })


def get_types(request):
    """Получить список всех типов"""
    types = DocumentTypes.objects.all().values('id', 'ru_name', 'en_name', 'ru_short', 'en_short')
    # Добавляем количество связанных подтипов
    for type_obj in types:
        type_obj['sub_types_count'] = DocumentTypes.objects.get(id=type_obj['id']).sub_types.count()

    return JsonResponse({'types': list(types)})


def get_all_subtypes(request):
    """Получить список всех подтипов"""
    subtypes = DocumentSubType.objects.all().values('id', 'name')
    return JsonResponse({'subtypes': list(subtypes)})


def get_relations(request):
    """Получить список всех связей между типами и подтипами"""
    relations = []
    types = DocumentTypes.objects.prefetch_related('sub_types').all()

    for doc_type in types:
        for subtype in doc_type.sub_types.all():
            relations.append({
                'type_id': doc_type.id,
                'type_name': doc_type.ru_name,
                'subtype_id': subtype.id,
                'subtype_name': subtype.name
            })

    return JsonResponse({'relations': relations})