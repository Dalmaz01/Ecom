import json

from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
from django.http.response import JsonResponse
import datetime

from .utils import cookieCart, cartData, guestOrder

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    products = models.Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)


def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    orderitems = data['orderitems']

    context = {
        'order': order,
        'orderitems': orderitems,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    orderitems = data['orderitems']

    context = {
        'order': order,
        'orderitems': orderitems,
        'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)


# def login(request):
#     return render(request, 'store/login.html', {})
#
#
# def register(request):
#     return render(request, 'store/register.html', {})


def productDetail(request, pk):
    product = models.Product.objects.get(pk=pk)
    print("success")
    return render(request, 'store/product_detail.html', {'product': product})


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    product = models.Product.objects.get(pk=productId)
    orderitem, created = models.OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()
    return JsonResponse('Item was updated..', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        models.ShippingInfo.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted', safe=False)


def register_page(request):
    '''
    ????????????????????, ???????????????????? ???? ????????????:
    - ?????????????????????? ???????????????? ??????????????????????
    - ?????????????????????? ????????????????????????
    '''
    if request.method == "POST":
        # ?????????????????????? ???????????????????????? ?????? POST ??????????????
        try:
            username = request.POST.get("login", None)
            password = request.POST.get("password", None)
            email = request.POST.get("email", None)
            first_name = request.POST.get("first_name", None)
            last_name = request.POST.get("last_name", None)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            customer = models.Customer.objects.create(
                user=user,
                name=first_name,
                email=email
            )
            return redirect(reverse('store:login'))
        except Exception as exc:
            print("?????? ???????????????? ???????????????????????? ?????????????????? ????????????", request.POST, exc)
            error = {
                'error_code': exc,
                'message': '?????????????????? ???????????????????????? ?????????????????? ????????????'
            }
            return render(request, 'store/register.html', {"error": error})

    # ???????????????????? ???????????????? ?????????????????????? ?????? GET ??????????????
    return render(request, 'store/register.html', {})


def login_page(request):
    '''
        ????????????????????, ???????????????????? ???? ????????????:
        - ?????????????????????? ???????????????? ????????????
        - ???????????????????????????? ????????????????????????
    '''
    if request.method == "GET":
        return render(request, "store/login.html", {})
    #if request.method == "POST":
    else:
        # ???????????????????????????? ???????????????????????? ?????? POST ??????????????
        username = request.POST.get("login", None)
        password = request.POST.get("password", None)
        user = authenticate(request, username=username, password=password)

        # ???????? ???????????????????????? ???????????????????? ?? ???????????? ??????????: ?????????????????????????? ?? ???????????????? ??????????????
        if user:
            login(request, user)
            return redirect(reverse("store:store"))

        # ???????? ???????????? ??????????????: ???????????????????? ?????????????????? ?? ???????????????????????? ????????????
        return render(request, "store/login.html", {"error": "???????????????????????? ?????????? ?????? ????????????"})


def logout_view(request):
    '''
        ????????????????????, ???????????????????? ???? ????????????:
        - ???????????? ???? ????????????????
    '''
    logout(request)
    return redirect(reverse('store:store'))