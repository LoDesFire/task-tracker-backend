from rest_framework.routers import SimpleRouter

from api.todo.view_sets import ProjectsViewSet
from api.todo.view_sets.tasks_view_set import TasksViewSet

router = SimpleRouter(trailing_slash=False)

router.register(r"tasks", TasksViewSet)
router.register(r"projects", ProjectsViewSet, basename="projects")
