from django.urls import path
from . import views
from .views import UserListView

app_name = 'main'

urlpatterns = [
    path('', views.popular_list, name='popular_list'),
    path('shop/', views.product_list, name= 'product_list'),
    path('shop/<slug:slug>/', views.product_detail,
        name='product_detail'),
    path('shop/category/<slug:category_slug>/', views.product_list,
         name= 'product_list_by_category'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/add/', views.product_add, name='product_add'),
    path('admin-panel/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('admin-panel/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('admin-panel/report/excel/', views.export_excel, name='export_excel'),
    path('admin-panel/report/pdf/', views.export_pdf, name='export_pdf'),
    path('admin_panel/users/', UserListView.as_view(), name='user_list'),
]

