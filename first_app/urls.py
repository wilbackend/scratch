from django.urls import path

from .views import product_list_create, product_update, product_delete

app_name = "first_app"

urlpatterns = [
    path("", product_list_create, name="home"),
    path("products/", product_list_create, name="products"),
    path("products/<int:pk>/edit/", product_update, name="product_edit"),
    path("products/<int:pk>/delete/", product_delete, name="product_delete"),
]
