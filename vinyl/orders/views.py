from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.core.mail import send_mail
from django.conf import settings 


def order_create(request):
    if request.user.is_staff:
        return redirect('shop') 
    cart = Cart(request)
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = OrderCreateForm(request.POST, request=request)
            if form.is_valid():
                order = form.save()

                # Отправка письма
                send_mail(
                    subject='Подтверждение заказа',
                    message=f'Ваш заказ №{order.id} оформлен. Спасибо!',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                )

                for item in cart:
                    discounted_price = item['product'].sell_price()
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=discounted_price,
                        quantity=item['quantity']
                    )
                cart.clear()
                return redirect('orders:order_successful', order_id=order.id)
        else:
            messages.warning(request, 'Пожалуйста, авторизуйтесь, чтобы сделать заказ.')
            return redirect('users:login')
    else:
        form = OrderCreateForm(request=request)

    return render(request, 'orders/order/create.html', {
        'cart': cart,
        'form': form,
        'message': 'Пожалуйста, заполните форму для оформления заказа.'
    })


def order_successful(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_successful.html', {'order': order})
