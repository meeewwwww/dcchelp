import re

from django import template
from bs4 import BeautifulSoup
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def html_to_text(html_content):
    """Конвертирует HTML в чистый текст"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(' ', strip=True)
    return text


@register.filter
def highlight_search(text, query):
    if not query or not text:
        return text

    # Экранируем специальные символы для regex
    pattern = re.escape(query)
    # Игнорируем регистр
    regex = re.compile(pattern, re.IGNORECASE)

    def replace(match):
        return f'<span class="highlight">{match.group()}</span>'

    highlighted = regex.sub(replace, str(text))
    return mark_safe(highlighted)