import json
from . import models


def cookieCart(request):
    try:
            cart = json.loads(request.COOKIES['cart'])
    except:
         cart = {}
    print('Cart:', cart)
    order = {
        'get_cart_items': 0,
        'get_cart_total': 0,
        'shipping': False,
    }
    orderitems = []
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = models.Product.objects.get(pk=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_items'] += cart[i]['quantity']
            order['get_cart_total'] += total

            orderitem = {
                'product':{
                    'id':product.pk,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL
                },
                'quantity':cart[i]['quantity'],
                'get_total':total
            }
            orderitems.append(orderitem)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems':cartItems, 'order': order, 'orderitems':orderitems}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        orderitems = cookieData['orderitems']

    return {'cartItems':cartItems, 'order': order, 'orderitems':orderitems}


def guestOrder(request, data):
    print('user is not logged in')

    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    orderitems = cookieData['orderitems']

    customer, created = models.Customer.objects.get_or_create(
        email=email
    )
    
    customer.name = name
    customer.save()

    order = models.Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in orderitems:
        product = models.Product.objects.get(id=item['product']['id'])

        orderItem = models.OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order