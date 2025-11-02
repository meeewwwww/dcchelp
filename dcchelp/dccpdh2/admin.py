from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'answered')
    list_display_links = ('question', )
    list_editable = ('answer', 'answered')
    list_per_page = 10

