from django.urls import path, include
from tasks.views import *



urlpatterns = [
    #task creation - admin
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    #user task details
    path('tasks/list/', TaskListView.as_view(), name='task-list'),
    path('tasks/update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/report/<int:pk>/', TaskReportView.as_view(), name='task-report'),   
]