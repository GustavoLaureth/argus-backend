from django.urls import path
from . import views

urlpatterns = [
  path("dashboard/", views.dashboard, name="dashboard"),
  path("create/", views.create, name="create"),
  path("history/", views.history, name="history"),
  path("subscription/", views.subscription, name="subscription"),
  path("profile/", views.profile, name="profile"),
]