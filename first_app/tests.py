from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Customer, Order, OrderItem, Product


class ProductCreateTest(TestCase):
    def test_create_product_with_valid_data(self):
        url = reverse("first_app:products")
        data = {
            "name": "Mechanical Keyboard",
            "price": "59.90",
            "is_active": "on",
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, url)
        self.assertEqual(Product.objects.count(), 1)

        product = Product.objects.first()
        self.assertEqual(product.name, "Mechanical Keyboard")
        self.assertEqual(str(product.price), "59.90")
        self.assertTrue(product.is_active)

    def test_cannot_delete_product_with_order_items(self):
        customer = Customer.objects.create(name="Ana", email="ana@example.com")
        product = Product.objects.create(
            name="Monitor",
            price=Decimal("120.00"),
            is_active=True,
        )
        order = Order.objects.create(customer=customer)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=product.price,
        )

        response = self.client.post(reverse("first_app:product_delete", args=[product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cannot delete this product because it already appears in orders.",
        )
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())


class OrderCreateFlowTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Ana", email="ana@example.com")
        self.product_one = Product.objects.create(
            name="Mouse",
            price=Decimal("19.99"),
            is_active=True,
        )
        self.product_two = Product.objects.create(
            name="USB Cable",
            price=Decimal("5.00"),
            is_active=True,
        )

    def _order_payload(self, rows):
        payload = {
            "order-customer": str(self.customer.pk),
            "items-TOTAL_FORMS": "3",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
        }

        for index, (product, quantity) in enumerate(rows):
            payload[f"items-{index}-product"] = str(product.pk)
            payload[f"items-{index}-quantity"] = str(quantity)

        for index in range(len(rows), 3):
            payload[f"items-{index}-product"] = ""
            payload[f"items-{index}-quantity"] = ""

        return payload

    def test_create_order_with_item_snapshot_prices(self):
        url = reverse("first_app:orders")

        response = self.client.post(
            url,
            self._order_payload(
                [
                    (self.product_one, 2),
                    (self.product_two, 1),
                ]
            ),
        )

        self.assertRedirects(response, url)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)

        order = Order.objects.get()
        first_item = order.items.get(product=self.product_one)
        self.assertEqual(first_item.unit_price, Decimal("19.99"))
        self.assertEqual(order.total_amount, Decimal("44.98"))

        self.product_one.price = Decimal("99.99")
        self.product_one.save(update_fields=["price"])
        first_item.refresh_from_db()

        self.assertEqual(first_item.unit_price, Decimal("19.99"))

    def test_rejects_duplicate_product_in_same_order(self):
        url = reverse("first_app:orders")

        response = self.client.post(
            url,
            self._order_payload(
                [
                    (self.product_one, 1),
                    (self.product_one, 3),
                ]
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Each product can appear only once per order.")
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_delete_order_removes_order_and_items(self):
        order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=order,
            product=self.product_one,
            quantity=2,
            unit_price=self.product_one.price,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product_two,
            quantity=1,
            unit_price=self.product_two.price,
        )

        response = self.client.post(reverse("first_app:order_delete", args=[order.pk]))

        self.assertRedirects(response, reverse("first_app:orders"))
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())
        self.assertEqual(OrderItem.objects.filter(order_id=order.pk).count(), 0)

    def test_order_delete_rejects_get(self):
        order = Order.objects.create(customer=self.customer)

        response = self.client.get(reverse("first_app:order_delete", args=[order.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Order.objects.filter(pk=order.pk).exists())


class CustomerCrudFlowTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Ana", email="ana@example.com")

    def test_create_customer(self):
        url = reverse("first_app:customers")

        response = self.client.post(
            url,
            {
                "name": "Luis",
                "email": "luis@example.com",
            },
        )

        self.assertRedirects(response, url)
        self.assertTrue(Customer.objects.filter(email="luis@example.com").exists())

    def test_update_customer(self):
        url = reverse("first_app:customer_edit", args=[self.customer.pk])

        response = self.client.post(
            url,
            {
                "name": "Ana Maria",
                "email": "ana.maria@example.com",
            },
        )

        self.assertRedirects(response, reverse("first_app:customers"))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Ana Maria")
        self.assertEqual(self.customer.email, "ana.maria@example.com")

    def test_delete_customer_without_orders(self):
        url = reverse("first_app:customer_delete", args=[self.customer.pk])

        response = self.client.post(url)

        self.assertRedirects(response, reverse("first_app:customers"))
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())

    def test_cannot_delete_customer_with_orders(self):
        Order.objects.create(customer=self.customer)
        url = reverse("first_app:customer_delete", args=[self.customer.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cannot delete this customer because it already has orders.",
        )
        self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists())
