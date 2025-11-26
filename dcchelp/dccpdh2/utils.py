class DataMixin:
    """Миксин, добавляющий в контекст названия и ссылки на разделы по всему сайту"""
    menu = [
        {'title': 'Главная', 'url_name': 'home'},
        {'title': 'Задачи', 'url_name': 'tasks'},
        {'title': 'Лист изменений', 'url_name': 'list_of_changes'},
        {'title': 'Оформление документации', 'url_name': 'documentation'},
        {'title': 'FAQ', 'url_name': 'FAQ'},
    ]

    def get_mixin_context(self, context, **kwargs):
        context['menu'] = self.menu
        context['title'] = self.title
        context.update(kwargs)
        return context
