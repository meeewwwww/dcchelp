from django.contrib import admin

# Register your models here.
from .models import Change


@admin.register(Change)
class ChangeAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'active', 'created', 'updated')
    list_display_links = ('title', )
    ordering = ('active', '-created')
    list_editable = ('active', )
    list_per_page = 10