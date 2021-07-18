from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotAllowed
from django.middleware import csrf
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

import datetime

from .forms import AddProduct, LoginForm, Search
from .models import Product, OrderProduct, Order, ClientAdress
from .utils import create_invoice, send_email_with_invoice


def log_in(request):
    args = {'csrf': csrf.get_token(request)}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        args['form'] = form
        username = form['username']
        password = form['password']
        auth_user = authenticate(form, username=username.value(), password=password.value())
        if auth_user is not None:
            login(request, user=auth_user)
            return HttpResponseRedirect('/')
    elif request.method == 'GET':
        args['form'] = LoginForm
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    return render(request, 'login.html', args)


@login_required
def log_out(request):
    logout(request)
    return HttpResponseRedirect('/')


def products_list(request):
    all_products = Product.objects.all().order_by('name')
    paginator = Paginator(all_products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, "categories.html", {'products': products})


def search(request):
    args = {'csrf': csrf.get_token(request)}
    if request.method == 'POST':
        form = Search(request.POST)
        args['form'] = form
        search_phrase = form['phrase'].value()
        if search_phrase is not None:
            found_products = Product.objects.filter(name__icontains=search_phrase).order_by('name') \
                       | Product.objects.filter(producer__icontains=search_phrase).order_by('name')
            paginator = Paginator(found_products, 12)
            page = request.GET.get('page')
            products = paginator.get_page(page)
            args['products'] = products
    elif request.method == 'GET':
        args['form'] = Search
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    return render(request, 'search.html', args)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "single.html", {'product': product})


@login_required
def add_product(request):
    args = {'csrf': csrf.get_token(request)}
    if request.user.is_staff and request.method == 'POST':
        form = AddProduct(request.POST, request.FILES)
        args['form'] = form
        if form.is_valid():
            product = Product(name=form['name'].value(), producer=form['producer'].value(),
                              description=form['description'].value(), price=form['price'].value(),
                              image=form['image'].value())
            product.save()
    elif request.user.is_staff and request.method == 'GET':
        args['form'] = AddProduct
    elif request.user.is_staff:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    else:
        return HttpResponseForbidden()
    return render(request, "add_product.html", args)


@login_required
def delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.user.is_staff:
        product.delete()
        return HttpResponseRedirect('/products/')
    else:
        return HttpResponseForbidden()


@login_required
def confirm_product_deletion(request, slug):
    product = get_object_or_404(Product, slug=slug)
    args = {'product': product}
    return render(request, 'confirm_product_deletion.html', args)


@login_required
def edit_product(request, slug):
    args = {'csrf': csrf.get_token(request)}
    product = get_object_or_404(Product, slug=slug)
    args['product'] = product
    if request.user.is_staff and request.method == 'POST':
        form = AddProduct(request.POST, request.FILES)
        args['form'] = form
        if form.is_valid():
            product.name = form['name'].value()
            product.producer = form['producer'].value()
            product.description = form['description'].value()
            product.price = form['price'].value()
            product.image = form['image'].value()
            product.save()
            return HttpResponseRedirect('/products/details/{}'.format(product.slug))
    elif request.user.is_staff and request.method == 'GET':
        form = AddProduct(instance=product)
        args['form'] = form
    elif request.user.is_staff:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    else:
        return HttpResponseForbidden()
    return render(request, "edit_product.html", args)


@login_required
def add_product_to_cart(request, slug):
    if request.user and not request.user.is_staff:
        product = get_object_or_404(Product, slug=slug)
        order_product, created = OrderProduct.objects.get_or_create(product=product, user=request.user, ordered=False)
        current_order = Order.objects.filter(user=request.user, ordered=False)
        if current_order.exists():
            order = current_order[0]
            if order.products.filter(product__slug=product.slug).exists():
                order_product.quantity += 1
                order_product.save()
            else:
                order.products.add(order_product)
            order.value += product.price
            order.save()
        else:
            ordered_time = timezone.now()
            order = Order.objects.create(user=request.user, ordered_time=ordered_time, ordered=False)
            order.products.add(order_product)
            order.value += product.price
            order.save()
        return HttpResponseRedirect('/products/cart')  # wypelnic
    else:
        return HttpResponseForbidden()


@login_required
def cart(request):
    args = {}
    if request.user:
        if request.user.is_staff:
            HttpResponseForbidden()
        else:
            current_order = Order.objects.filter(user=request.user, ordered=False)
            if current_order.exists():
                args['value'] = current_order[0].value
                ordered_products = current_order[0].products.all()
                args['products'] = ordered_products
    else:
        HttpResponseForbidden()
    return render(request, "cart.html", args)


@login_required
def remove_product_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    current_order = Order.objects.filter(user=request.user, ordered=False)
    if current_order.exists():
        order = current_order[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderProduct.objects.filter(product=product, user=request.user, ordered=False)[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order.value -= order_product.product.price
                order_product.save()
                order.save()
            else:
                order.value -= order_product.product.price
                order.products.remove(order_product)
                order.save()
            return HttpResponseRedirect('/products/cart')
        return HttpResponseRedirect('/products/cart')


@login_required
def confirm_order(request):
    if request.user:
        if request.user.is_staff:
            HttpResponseForbidden()
        else:
            current_order = Order.objects.filter(user=request.user, ordered=False)
            if current_order.exists():
                order = current_order[0]
                order.ordered_time = timezone.now()
                order.payment_time = order.ordered_time + datetime.timedelta(days=14)
                order.ordered = True
                client = get_object_or_404(ClientAdress, client=order.user)
                create_invoice(template_src='pdf/invoice.html', order=order, client=client)
                order.save()
                send_email_with_invoice(order)
                return render(request, "order_confirmed.html")
    else:
        HttpResponseForbidden()
    return render(request, "order_confirmed.html")
