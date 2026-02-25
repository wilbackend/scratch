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
