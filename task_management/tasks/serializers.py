from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_to_username',
            'created_by', 'created_by_username', 'due_date', 'status',
            'completion_report', 'worked_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate(self, data):
        if 'status' in data and data['status'] == 'completed':
            if not data.get('completion_report'):
                raise serializers.ValidationError(
                    {"completion_report": "Completion report is required when marking a task as completed"}
                )
            if not data.get('worked_hours'):
                raise serializers.ValidationError(
                    {"worked_hours": "Worked hours must be provided when marking a task as completed"}
                )
        return data

class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'assigned_to_username', 'completion_report', 'worked_hours', 'status']
        read_only_fields = ['id', 'title', 'assigned_to_username', 'status']
    
    def validate(self, data):
        if self.instance.status != 'completed':
            raise serializers.ValidationError("Task must be completed to view its report")
        return data