import logging
from rest_framework import viewsets
from tasks.filters import TaskFilter
from .serializers import TaskSerializer
from .models import Task
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
