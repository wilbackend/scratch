from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST

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


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("first_app:products")
    else:
        form = ProductForm(instance=product)

    products = Product.objects.all()
    return render(
        request,
        "first_app/products.html",
        {"form": form, "products": products, "editing_product": product},
    )

@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("first_app:products")
