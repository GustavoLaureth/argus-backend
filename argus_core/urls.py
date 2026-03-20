from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
  path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
  path("dashboard/", views.dashboard, name="dashboard")
]