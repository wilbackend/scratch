from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CustomerForm, OrderCreateForm, OrderItemFormSet, ProductForm
from .models import Order, OrderItem, Product, Customer
from django.db.models.deletion import ProtectedError

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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order_items = product.order_items.select_related("order__customer").order_by(
        "-order__ordered_at",
        "-order_id",
    )
    order_count = order_items.count()
    total_quantity_sold = sum((item.quantity for item in order_items), 0)
    total_revenue = sum((item.line_total for item in order_items), Decimal("0.00"))
    return render(
        request,
        "first_app/product_detail.html",
        {
            "product": product,
            "order_items": order_items,
            "order_count": order_count,
            "total_quantity_sold": total_quantity_sold,
            "total_revenue": total_revenue,
        },
    )


def order_list_create(request):
    if request.method == "POST":
        order_form = OrderCreateForm(request.POST, prefix="order")
        item_formset = OrderItemFormSet(request.POST, prefix="items")

        if order_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                order = order_form.save()
                for item_form in item_formset:
                    if not item_form.cleaned_data:
                        continue

                    product = item_form.cleaned_data.get("product")
                    quantity = item_form.cleaned_data.get("quantity")
                    if not product or quantity in (None, ""):
                        continue

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                    )
            return redirect("first_app:orders")
    else:
        order_form = OrderCreateForm(prefix="order")
        item_formset = OrderItemFormSet(prefix="items")

    orders = (
        Order.objects.select_related("customer")
        .prefetch_related("items__product")
        .order_by("-ordered_at", "-id")
    )
    return render(
        request,
        "first_app/orders.html",
        {
            "order_form": order_form,
            "item_formset": item_formset,
            "orders": orders,
        },
    )


@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect("first_app:orders")


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
    try:
        product.delete()
        return redirect("first_app:products")
    except ProtectedError:
        form = ProductForm()
        products = Product.objects.all()
        return render(
            request,
            "first_app/products.html",
            {
                "form": form,
                "products": products,
                "delete_error": "Cannot delete this product because it already appears in orders.",
            },
        )

def customer_list_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("first_app:customers")
    else:
        form = CustomerForm()

    search_term = request.GET.get("q", "").strip()
    customers = Customer.objects.order_by("name")
    if search_term:
        customers = customers.filter(
            Q(name__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(phone__icontains=search_term)
        )

    return render(
        request,
        "first_app/customers.html",
        {"form": form, "customers": customers, "search_term": search_term},
    )

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("first_app:customers")
    else:
        form = CustomerForm(instance=customer)

    customers = Customer.objects.order_by("name")
    return render(
        request,
        "first_app/customers.html",
        {"form": form, "customers": customers, "editing_customer": customer},
    )

@require_POST
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    try:
        customer.delete()
        return redirect("first_app:customers")
    except ProtectedError:
        form = CustomerForm()
        customers = Customer.objects.order_by("name")
        return render(
            request,
            "first_app/customers.html",
            {
                "form": form,
                "customers": customers,
                "delete_error": "Cannot delete this customer because it already has orders.",
            },
        )

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.prefetch_related("items__product").order_by("-ordered_at", "-id")
    order_count = orders.count()
    return render(
        request,
        "first_app/customer_detail.html",
        {
            "customer": customer,
            "orders": orders,
            "order_count": order_count,
        },
    )
