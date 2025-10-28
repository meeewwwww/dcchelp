from django.forms import ModelForm, ValidationError

from .models import Change


class ChangeForm(ModelForm):
    class Meta:
        model = Change
        fields = ['number', 'title', 'text', 'link_approvement']

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        empty_values = ['', '<br>', '<p></p>', '<div><br></div>', '<p><br></p>']

        if not text or text in empty_values:
            raise ValidationError('Описание изменения обязательно')
        return text