from django.shortcuts import render
from django.views.generic.detail import DetailView

# Create your views here.
def home(request):
    return render(request, 'main/home.html')
