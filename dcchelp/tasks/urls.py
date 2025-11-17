from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.TasksView.as_view(), name='tasks'),  # GET запросы
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/archive/', views.archive_statistics, name='archive_statistics'),
    path('tasks/archive/get-statistics/', views.get_statistics_data, name='get_statistics_data'),
    path('tasks/archive/export-excel/', views.export_to_excel, name='export_to_excel'),
    path('tasks/archive/search-tasks/', views.search_tasks, name='search_tasks'),
    path('tasks/archive/update-task/<int:task_id>/', views.update_task, name='update_task'),
]