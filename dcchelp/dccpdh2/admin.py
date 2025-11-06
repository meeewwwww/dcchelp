from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')
    list_display_links = ('question', )
    list_editable = ('answer', )
    list_per_page = 10

