from rest_framework import  status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from tasks.models import Task
from tasks.serializers import TaskSerializer
from user.permissions import *
from rest_framework.exceptions import PermissionDenied, NotFound

from rest_framework.views import APIView
#task creation admin or super admin
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin():
            return Task.objects.all()
        elif user.is_admin():
            return Task.objects.filter(created_by=user) | Task.objects.filter(assigned_to__managed_by=user)
        else:
            return Task.objects.filter(assigned_to=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_admin():  
            return Response(
                {"detail": "You do not have permission to create tasks."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Task.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.data.get('status') == 'completed':
            if not request.data.get('completion_report'):
                return Response(
                    {"completion_report": "Completion report is required when marking a task as completed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not request.data.get('worked_hours'):
                return Response(
                    {"worked_hours": "Worked hours must be provided when marking a task as completed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return super().update(request, *args, **kwargs)
#user task views
class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        task = super().get_object()
        if task.assigned_to != self.request.user:
            raise PermissionDenied("You can only update your own tasks.")
        return task

    def update(self, request, *args, **kwargs):
        task = self.get_object()

        if request.data.get('status') == 'completed':
            if not request.data.get('completion_report'):
                return Response(
                    {"completion_report": "Required when marking task as completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not request.data.get('worked_hours'):
                return Response(
                    {"worked_hours": "Required when marking task as completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return super().update(request, *args, **kwargs)


class TaskReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound("Task not found.")

        if task.status != 'completed':
            return Response(
                {"detail": "Report is only available for completed tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_admin():
            raise PermissionDenied("Only admins and superadmins can view task reports.")

        return Response({
            "task_id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to.username,
            "completion_report": task.completion_report,
            "worked_hours": task.worked_hours,
            "status": task.status
        })