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
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render






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
    template_name='main/address_list.html'

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
    template_name='main/address_form.html'
    success_url=reverse_lazy('address_list')

    def form_valid(self, form):
        obj=form.save(commit=False)
        obj.user=self.request.user
        obj.save()
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model=models.Address
    fields=[
        'name',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country',
    ]
    template_name='main/address_update.html'
    success_url=reverse_lazy('address_list')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
        #Each user must be able to operate only on their own address

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model=models.Address
    success_url=reverse_lazy('address_list')
    template_name='main/address_delete.html'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
#(LoginRequiredMixin, DeleteView)

def add_to_basket(request):
    product=get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket=request.basket#will work only if basket exists and its id is in
    #the session already
    if not request.basket:
        if request.user.is_authenticated:
            user=request.user
        else:
            user=None
        basket=models.Basket.objects.create(user=user)
        request.session['basket_id']=basket.id
    basketline, created=models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity+=1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product", args=(product.slug,))
    )


def manage_basket(request):
    if not request.basket:
        return render(request, "main/basket.html", {"formset":None})
    if request.method=="POST":
        formset=forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset=forms.BasketLineFormSet(
            instance=request.basket
        )
    if request.basket.is_empty():
        return render(request, "main/basket.html", {"formset":None})
    return render(request, "main/basket.html", {"formset":formset})

def create_order(self, billing_address, shipping_address):
    if not self.user:
        raise exceptions.BasketException(
            "Cannot create order without user"
        )
    logger.info(
        "Creating order for basket_id=%d"
        ", shipping_address_id=%d, billing_address_id=%d",
        self.id,
        shipping_address.id,
        billing_address.id,
    )
    order_data = {
            "user":self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zip_code": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country,
        }
    order = Order.objects.create(**order_data)
    c=0
    for line in self.basketline_set.all():
        for item in range(line.quantity):
            order_line_data = {
                    "order": order,
                    "product": line.product,
            }
            order_line = OrderLine.objects.create(
                    **order_line_data
            )
            c += 1
    logger.info(
            "Created order with id=%d and lines_count=%d",
            order.id,
            c,
        )
    self.status = Basket.SUBMITTED
    self.save()
    return order
