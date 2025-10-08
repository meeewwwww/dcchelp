menu = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'Процедуры', 'url_name': 'procedures'}, # Подумать над целесообразностью раздела
    {'title': 'Лист изменений', 'url_name': 'list_of_changes'},
    {'title': 'Оформление документации', 'url_name': 'documentation'},
    {'title': 'Запуск процессов', 'url_name': 'processes'}, # Подумать над целесообразностью раздела
    {'title': 'FAQ', 'url_name': 'FAQ'},
]


class DataMixin:
    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context['title'] = self.title
        context.update(kwargs)
        return context
