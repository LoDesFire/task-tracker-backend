from django.urls import include, path

from api import oauth, todo

urlpatterns = [
    path("todo/", include(todo.router.urls)),
    path("auth/", include(oauth.router.urls)),
    path("todo/", include(todo.project_router.urls)),
]
