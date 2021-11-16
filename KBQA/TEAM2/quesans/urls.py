from django.urls import path

from . import views


# url paths within the webapp
urlpatterns = [
    path("", views.base, name="base"),
    path("get_answer", views.get_answers, name="get_answers"),
]
