from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('groups/', views.group_list, name='group_list'),
    
    path('groups/create/', views.group_create, name='group_create'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
]