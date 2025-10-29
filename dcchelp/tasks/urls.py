from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.TasksView.as_view(), name='tasks'),
    ]