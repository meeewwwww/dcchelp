from django import forms
from .models import DocumentArticle, DocumentSubType, DocumentTypes, Change


class ChangeForm(forms.ModelForm):
    class Meta:
        model = Change
        fields = ['number', 'title', 'text', 'link_approvement']

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        empty_values = ['', '<br>', '<p></p>', '<div><br></div>', '<p><br></p>']

        if not text or text in empty_values:
            raise forms.ValidationError('Описание изменения обязательно')
        return text


class DocumentArticleForm(forms.ModelForm):
    doc_type = forms.ModelChoiceField(queryset=DocumentTypes.objects.all(), empty_label='Выберите тип', label='Тип документации')
    doc_sub_type = forms.ModelChoiceField(queryset=DocumentSubType.objects.none(), empty_label='Сначала выберите тип', label='Подтип документации/статьи')

    class Meta:
        model = DocumentArticle
        fields = ['title', 'text', 'doc_type', 'doc_sub_type']
        labels = {
            'title': 'Название',
            'text': 'Содержание',
        }
        widgets = {
            'text': forms.Textarea(),
        }

    def clean_doc_sub_type(self):
        # Пропускаем валидацию, так как подтипы загружаются через AJAX
        return self.cleaned_data['doc_sub_type']