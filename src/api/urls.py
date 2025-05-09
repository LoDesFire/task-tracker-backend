from django.urls import include, path

from api import todo

urlpatterns = [path("todo/", include(todo.router.urls))]
