from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
  return render(request, "pages/dashboard.html")

@login_required
def create(request):
  return render(request, "pages/create.html")

@login_required
def history(request):
  return render(request, "pages/history.html")

@login_required
def subscription(request):
  return render(request, "pages/subscription.html")

@login_required
def profile(request):
  return render(request, "pages/profile.html")