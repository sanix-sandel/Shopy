from django.urls import path
from . import models, views
from django.views.generic.detail import DetailView

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', DetailView.as_view(model=models.Product),
        name='product'),
]
