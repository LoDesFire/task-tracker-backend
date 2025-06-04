from django.urls import include, path

from api import todo

urlpatterns = [path("", include(todo.router.urls))]
