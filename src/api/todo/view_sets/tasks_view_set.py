from rest_framework.viewsets import ViewSet

from apps.todo.models import Tasks


class TasksViewSet(ViewSet):
    queryset = Tasks.objects.all()
    pass
