from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from dccpdh2.utils import DataMixin
from documentation.models import DocumentTypes, DocumentArticle, DocumentSubType
from documentation.forms import DocumentArticleForm, DocumentArticleEditForm


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
