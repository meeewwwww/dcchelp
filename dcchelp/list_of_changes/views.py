from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from dccpdh2.utils import DataMixin

from .forms import ChangeForm
from .models import Change


class ListOfChangesView(DataMixin, ListView):
    """ Раздел листа изменений """
    template_name = 'list_of_changes/list_of_changes.html'
    context_object_name = 'changes'
    title = 'Лист изменений'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)

    def get_queryset(self):
        return Change.objects.all()


""" add_change, edit_change, cancel_change, delete_change реализованы как функции для AJAX 
(обновление данных на странице без обновления самой страницы) """


def add_change(request):
    if request.method == 'POST':
        form = ChangeForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def edit_change(request, change_id):
    """ Редактирование пункта листа изменений """
    change = get_object_or_404(Change, id=change_id)

    if request.method == 'POST':
        form = ChangeForm(request.POST, instance=change)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    else:  # request.method == 'GET'
        return JsonResponse({
            'number': change.number,
            'title': change.title,
            'text': change.text,
            'link_approvement': change.link_approvement,
        })


def cancel_change(request, change_id):
    """ Отмена пункта листа изменений """
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.active = 0
        change.save()
        return JsonResponse({'success': True})


def delete_change(request, change_id):
    """ Удаление пункта листа изменений """
    if request.method == 'POST':
        change = get_object_or_404(Change, id=change_id)
        change.delete()
        return JsonResponse({'success': True})