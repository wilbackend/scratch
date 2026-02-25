from django.urls import path

from .views import order_list_create, product_delete, product_list_create, product_update, customer_list_create, customer_update, customer_delete

app_name = "first_app"

urlpatterns = [
    path("", product_list_create, name="home"),
    path("products/", product_list_create, name="products"),
    path("products/<int:pk>/edit/", product_update, name="product_edit"),
    path("products/<int:pk>/delete/", product_delete, name="product_delete"),
    path("orders/", order_list_create, name="orders"),
    path("customer/", customer_list_create, name="customers"),
    path("customer/<int:pk>/edit/", customer_update, name="customer_edit"),
    path("customers/<int:pk>/delete/", customer_delete, name="customer_delete"),
]
