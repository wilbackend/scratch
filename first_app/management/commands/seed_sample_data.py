import random
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from first_app.models import Customer, Order, OrderItem, Product

SAMPLE_CUSTOMERS = [
    {"name": "Ana Lopez", "email": "ana.lopez@example.com"},
    {"name": "Luis Romero", "email": "luis.romero@example.com"},
    {"name": "Carla Diaz", "email": "carla.diaz@example.com"},
    {"name": "Miguel Flores", "email": "miguel.flores@example.com"},
    {"name": "Sofia Martinez", "email": "sofia.martinez@example.com"},
    {"name": "Daniel Rivera", "email": "daniel.rivera@example.com"},
]

SAMPLE_PRODUCTS = [
    {"name": "Mechanical Keyboard", "price": Decimal("79.90"), "is_active": True},
    {"name": "Wireless Mouse", "price": Decimal("24.50"), "is_active": True},
    {"name": "27-inch Monitor", "price": Decimal("189.00"), "is_active": True},
    {"name": "USB-C Dock", "price": Decimal("129.00"), "is_active": True},
    {"name": "Notebook Stand", "price": Decimal("32.75"), "is_active": True},
    {"name": "Legacy Printer Cable", "price": Decimal("8.99"), "is_active": False},
]


class Command(BaseCommand):
    help = "Create sample customers, products, and orders for local exploration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--orders",
            type=int,
            default=5,
            help="Number of sample orders to create.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Seed for repeatable order generation.",
        )

    def handle(self, *args, **options):
        order_total = options["orders"]
        if order_total < 1:
            raise CommandError("--orders must be at least 1.")

        rng = random.Random(options["seed"])
        customers, created_customers = self._ensure_customers()
        products, created_products = self._ensure_products()
        active_products = [product for product in products if product.is_active]

        if not customers:
            raise CommandError("No customers are available for sample orders.")
        if not active_products:
            raise CommandError("No active products are available for sample orders.")

        created_orders, created_items = self._create_orders(
            customers=customers,
            active_products=active_products,
            order_total=order_total,
            rng=rng,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Sample data ready: "
                f"{created_customers} new customers, "
                f"{created_products} new products, "
                f"{created_orders} new orders, "
                f"{created_items} new order items."
            )
        )

    def _ensure_customers(self):
        customers = []
        created_total = 0

        for entry in SAMPLE_CUSTOMERS:
            customer, created = Customer.objects.get_or_create(
                email=entry["email"],
                defaults={"name": entry["name"]},
            )
            customers.append(customer)
            created_total += int(created)

        return customers, created_total

    def _ensure_products(self):
        products = []
        created_total = 0

        for entry in SAMPLE_PRODUCTS:
            product, created = Product.objects.get_or_create(
                name=entry["name"],
                defaults={
                    "price": entry["price"],
                    "is_active": entry["is_active"],
                },
            )
            products.append(product)
            created_total += int(created)

        return products, created_total

    def _create_orders(self, customers, active_products, order_total, rng):
        created_items = 0

        with transaction.atomic():
            for _ in range(order_total):
                customer = rng.choice(customers)
                order = Order.objects.create(customer=customer)
                item_total = rng.randint(1, min(3, len(active_products)))
                selected_products = rng.sample(active_products, k=item_total)

                for product in selected_products:
                    quantity = rng.randint(1, 4)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                    )
                    created_items += 1

        return order_total, created_items
