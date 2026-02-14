from django.urls import path

from .views import product_list_create

app_name = "first_app"

urlpatterns = [
    path("", product_list_create, name="home"),
    path("products/", product_list_create, name="products"),
]
