menu = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'Задачи', 'url_name': 'tasks'},
    {'title': 'Лист изменений', 'url_name': 'list_of_changes'},
    {'title': 'Оформление документации', 'url_name': 'documentation'},
    {'title': 'FAQ', 'url_name': 'FAQ'},
]


class DataMixin:
    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context['title'] = self.title
        context.update(kwargs)
        return context
