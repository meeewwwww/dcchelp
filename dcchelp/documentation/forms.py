from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from documentation.models import DocumentTypes, DocumentSubType, DocumentArticle


class DocumentArticleForm(forms.ModelForm):
    doc_type = forms.ModelChoiceField(queryset=DocumentTypes.objects.all(), empty_label='Выберите тип', label='Тип документации')
    doc_sub_type = forms.ModelChoiceField(queryset=DocumentSubType.objects.none(), empty_label='Сначала выберите тип', label='Подтип документации/статьи')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["text"].required = False

    class Meta:
        model = DocumentArticle
        fields = ['title', 'text', 'doc_type', 'doc_sub_type']
        labels = {
            'title': 'Название',
            'text': 'Содержание',
        }
        widgets = {
            "text": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="default"
              )
        }

    def clean_doc_sub_type(self):
        # Пропускаем валидацию, так как подтипы загружаются через AJAX
        return self.cleaned_data['doc_sub_type']


class DocumentArticleEditForm(forms.ModelForm):
    class Meta:
        model = DocumentArticle
        fields = ['title', 'text']