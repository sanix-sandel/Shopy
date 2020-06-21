from django.shortcuts import render
from .models import Product
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    FormView
)
from main import forms
from django.shortcuts import get_object_or_404
from . import models
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin



logger=logging.getLogger(__name__)

# Create your views here.
def home(request):
    return render(request, 'main/home.html')


class ProductView(DetailView):
    model=Product
    template_name='main/product_detail.html'



class ProductListView(ListView):
    model=Product
    paginate_by=4
    template_name='main/product_list.html'

    def get_queryset(self):
        tag=self.kwargs['tag']
        self.tag=None
        if tag != "all":
            self.tag=get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products=Product.objects.active().filter(tag=self.tag)
        else:
            products=models.Product.objects.active()
        return products.order_by("name")


class SignupView(FormView):
    template_name='main/signup.html'
    form_class=forms.UserCreationForm

    def get_success_url(self):
        redirect_to=self.request.GET.get('next', '/')
        return redirect_to

    def form_valid(self, form):
        response=super().form_valid(form)
        form.save()
        email=form.cleaned_data.get("email")
        raw_password=form.claned_data.get("password1")
        logger.info(
            "New signup for email=%s through SignUpView", email
        )
        user=authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_email()

        messages.info(
            self.request, "You signed up successfully"
        )
        return response



class AddressListView(LoginRequiredMixin, ListView):
    model=models.Address

    def get_queryset(self):
        return self.models.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model=models.Address
    fields=[
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country',
    ]
    success_url=reverse_lazy('address_list')

    def form_valid(self, form):
        obj=form.save(commit=False)
        obj.user=self.request.user
        obj.save()
        return super().form_valid(form)

    def form_valid(self, form):
        model=models.Address
        fields=[
            'name',
            'address1',
            'address2',
            'zip_code',
            'city',
            'country',
        ]


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model=models.Address
    success_url=reverse_lazy('address_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
#(LoginRequiredMixin, DeleteView)
