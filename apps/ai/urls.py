from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create, name="create"),
    path("history/", views.history, name="history"),
]