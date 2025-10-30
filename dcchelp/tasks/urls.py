from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.TasksView.as_view(), name='tasks'),  # GET запросы
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]