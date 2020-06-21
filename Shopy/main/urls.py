from django.urls import path
from . import models, views
from django.views.generic.detail import DetailView
from . import forms
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.ProductView.as_view(),
        name='product'),
    path('products/<slug:tag>/', views.ProductListView.as_view(),
        name='products'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(
            template_name='main/login.html',
            form_class=forms.AuthenticationForm,
        ),
        name='login',

    ),
]
