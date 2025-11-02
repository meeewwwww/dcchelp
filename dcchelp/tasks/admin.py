from django.contrib import admin

from .forms import TaskFrom
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ('number', 'created', 'name', 'priority', 'iteration', 'status', 'user', 'finished', 'result', 'comment'),
                "classes": ["wide"],
            },
        ),
    ]
    form = TaskFrom
    list_display = ('number', 'created_date', 'name', 'priority', 'iteration', 'status', 'user', 'finished', 'result')
    list_editable = ('name', 'priority', 'iteration', 'status', 'user', 'finished', 'result')
    list_display_links = ('number',)
    date_hierarchy = 'created'
    list_per_page = 30
