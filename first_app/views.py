from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

def product_list_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("first_app:products")
    else:
        form = ProductForm()

    products = Product.objects.all()
    return render(request, "first_app/products.html", {"form": form, "products": products})


