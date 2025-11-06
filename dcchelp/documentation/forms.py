from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from documentation.models import DocumentTypes, DocumentSubType, DocumentArticle


class DocumentArticleForm(forms.ModelForm):
    title = forms.CharField(label='Заголовок')
    doc_type = forms.ModelChoiceField(queryset=DocumentTypes.objects.all(), empty_label='Выберите тип', label='Тип документации')
    doc_sub_type = forms.ModelChoiceField(queryset=DocumentSubType.objects.none(), empty_label='Сначала выберите тип', label='Подтип документации / заметки')
    text = forms.CharField(widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"), label='Содержание')

    class Meta:
        model = DocumentArticle
        fields = ['title', 'text', 'doc_type', 'doc_sub_type']

    def clean_doc_sub_type(self):
        # Пропускаем валидацию, так как подтипы загружаются через AJAX
        return self.cleaned_data['doc_sub_type']


class DocumentArticleEditForm(forms.ModelForm):
    title = forms.CharField(label='Название')
    text = forms.CharField(widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
                           label='Содержание')

    class Meta:
        model = DocumentArticle
        fields = ['title', 'text']


class DocumentTypesEditForm(forms.ModelForm):
    ru_name = forms.CharField(label='Наименование', required=True, max_length=255)

    class Meta:
        model = DocumentTypes
        fields = ['ru_name', 'sub_types']
        labels = {
            'sub_types': 'Связанные подкатегории'
        }


class DocumentSubTypeEditForm(forms.ModelForm):
    class Meta:
        model = DocumentSubType
        fields = ['name']
        labels = {
            'name': 'Подтип',
        }