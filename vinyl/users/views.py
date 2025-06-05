from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserLoginForm, UserRegistrationForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from orders.models import Order, OrderItem


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                messages.success(request, 'Вы успешно вошли в систему')
                return HttpResponseRedirect(reverse('main:product_list'))
        else:
            messages.error(request, 'Ошибка входа. Проверьте данные')
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Авторизация'
    }
    return render(request, 'users/login.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            auth.login(request, user)
            messages.success(request, f'{user.username}, вы успешно зарегистрировались!')
            return redirect('user:profile')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Регистрация'
    }
    return render(request, 'users/registration.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return HttpResponseRedirect(reverse('user:profile'))
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
    else:
        form = ProfileForm(instance=request.user)
    
    orders = Order.objects.filter(user=request.user).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product'),
        )
    ).order_by('-id')
    
    context = {
        'form': form,
        'orders': orders,
        'title': 'Личный кабинет'
    }
    return render(request, 'users/profile.html', context)


def logout(request):
    auth.logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect(reverse('main:product_list'))