from rest_framework_nested import routers

from api.todo.view_sets import ProjectsViewSet
from api.todo.view_sets.project_permissions_view_set import (
    ProjectUserPermissionsViewSet,
)
from api.todo.view_sets.tasks_view_set import TasksViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"projects", ProjectsViewSet, basename="projects")

project_router = routers.NestedSimpleRouter(
    parent_router=router,
    parent_prefix="projects",
    lookup="projects",
)
project_router.register(r"tasks", TasksViewSet, basename="tasks")

project_router.register(
    r"permissions", ProjectUserPermissionsViewSet, basename="permissions"
)
