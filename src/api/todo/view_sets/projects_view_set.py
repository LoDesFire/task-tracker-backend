from rest_framework.viewsets import ViewSet

from apps.todo.models import Projects


class ProjectsViewSet(ViewSet):
    queryset = Projects.objects.all()
    pass
