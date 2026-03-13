from django.shortcuts import render

def dashboard(request):
  return render(request, "pages/dashboard.html")

def create(request):
  return render(request, "pages/create.html")

def history(request):
  return render(request, "pages/history.html")

def subscription(request):
  return render(request, "pages/subscription.html")

def profile(request):
  return render(request, "pages/profile.html")