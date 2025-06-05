from django.urls import path
from . import views
from .views import order_successful

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('success/<int:order_id>/', views.order_successful, name='order_successful'),
]
