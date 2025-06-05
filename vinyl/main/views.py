from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from cart.forms import CartAddProductForm
from orders.models import Order, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .forms import ProductForm 
from django.contrib import messages
import io
import pandas as pd
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils.dateparse import parse_date
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def popular_list(request):
    products = Product.objects.filter(available=True)[:3]
    return render(request,
                  'main/index/index.html',
                  {'products': products})
    
    
def product_detail(request, slug):
    product = get_object_or_404(Product,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm
    return render(request,
                  'main/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})

def product_list(request, category_slug=None):
    page = request.GET.get('page', 1)
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    paginator = Paginator(products, 10)
    current_page = paginator.page(int(page))
    if category_slug:
        category = get_object_or_404(Category,
                                     slug=category_slug)
        paginator = Paginator(products.filter(category=category), 10)
        current_page = paginator.page(int(page))
    return render(request, 
                  'main/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': current_page, 
                   'slug_url': category_slug})
    



# проверка на админа
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    return render(request, 'admin_panel/dashboard.html', {
        'products': products,
        'orders': orders,
    })


@login_required
@user_passes_test(is_admin)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            from django.utils.text import slugify
            product.slug = slugify(product.name)
            product.save()
            messages.success(request, 'Товар успешно добавлен.')
            return redirect('main:admin_panel')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/product_form.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        product = form.save(commit=False)

        from django.utils.text import slugify
        # Генерировать слаг, только если он пустой
        if not product.slug:
            product.slug = slugify(product.name)

        product.save()
        messages.success(request, 'Товар успешно отредактирован.')
        return redirect('main:admin_panel')
    return render(request, 'admin_panel/product_form.html', {'form': form})



@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Товар успешно удалён.')
    return redirect('main:admin_panel')


# отчеты
@login_required
@user_passes_test(is_admin)
def export_excel(request):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    start = parse_date(start_str) if start_str else None
    end = parse_date(end_str) if end_str else None

    orders = Order.objects.all()

    if start and end:
        orders = orders.filter(created__date__range=(start, end))

    data = []
    for o in orders:
        data.append({
            'ID': o.id,
            'Дата': o.created.strftime('%Y-%m-%d'),
            'Сумма': o.total_price
        })

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Отчёт')
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='report.xlsx')


def export_pdf(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    orders = Order.objects.filter(created__date__range=[start, end])

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # Регистрация шрифта для кириллицы
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    p.setFont("Arial", 14)

    p.drawString(50, 800, f"Отчет о заказах с {start} по {end}")

    # Таблица
    data = [["ID", "Дата", "Сумма"]]
    for order in orders:
        data.append([str(order.id), order.created.strftime("%Y-%m-%d"), str(order.total_price)])

    table = Table(data, colWidths=[100, 200, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Сдвиг вниз
    table.wrapOn(p, 50, 700)
    table.drawOn(p, 50, 700 - 25 * len(data))

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return User.objects.filter(is_staff=False)