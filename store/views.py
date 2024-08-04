from django.shortcuts import render
from .models import *
import datetime
from django.http import JsonResponse
import json
from .utils import cookieCart , cartData , guestOrder

# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context = {'products':products , 'cartItems': cartItems}
    return render(request , 'store/store.html' , context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items , 'order': order ,'cartItems': cartItems}
    return render(request , 'store/cart.html' , context)      


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items , 'order': order,'cartItems': cartItems}
    return render(request , 'store/checkout.html' , context)


def updateItem(request):
    data = json.loads(request.body)
    print('Received data:', data)
    productId = data.get('productId')
    action = data.get('action')
    print('Action:', action)
    print('Product ID:', productId)

    try:
        customer = request.user.customer
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1

        orderItem.save()
        if orderItem.quantity <= 0:
            orderItem.delete()

        return JsonResponse({'message': 'Item updated'}, status=200)
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'},status=400)
    except Exception as e:
        print('Error:', e)
        return JsonResponse({'error': 'An error occurred'},status=500)
    
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
            
    else:
       customer , order = guestOrder(request , data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
            order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer= customer,
            order=order,
            address= data['shipping']['address'],
            city =data['shipping']['city'],
            state =data['shipping']['state'],
            zipcode =data['shipping']['zipcode'],
        )

             
    
    return JsonResponse('Payment Completed!', safe = False)