from django import forms
from .models import Product, Order
from django.forms import BaseFormSet, formset_factory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "is_active"]

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer"]


class OrderItemInputForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none())
    quantity = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")

class BaseOrderItemInputFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        seen_products = set()
        item_count = 0

        for form in self.forms:
            if not form.cleaned_data:
                continue

            product = form.cleaned_data.get("product")
            quantity = form.cleaned_data.get("quantity")

            if not product or quantity in (None, ""):
                continue

            item_count += 1

            if product.pk in seen_products:
                form.add_error("product", "Each product can appear only once per order.")
            seen_products.add(product.pk)

        if item_count == 0:
            raise forms.ValidationError("Add at least one item to create an order.")

OrderItemFormSet = formset_factory(
    OrderItemInputForm,
    formset=BaseOrderItemInputFormSet,
    extra=3,
)
