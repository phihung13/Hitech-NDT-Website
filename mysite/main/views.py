from django.shortcuts import render

# myapp/views.py
from django.http import HttpResponse

# main/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def news(request):
    return render(request, 'main/news.html')

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    return render(request, 'main/contact.html')