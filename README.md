# Sales Tracker Database (Django)

A Django practice project for learning how forms, views, models, and the SQLite database work together in a small sales tracker.

## Current Scope

- Product create, list, update, and delete
- Customer create, list, update, and delete
- Order create with multiple order items
- Order delete with cascading order-item removal
- Protected deletes for customers and products already used by orders
- Sample data loading command for local exploration
- SQLite database (`db.sqlite3`)

## Tech Stack

- Python
- Django 6
- SQLite

## Project Structure

- `first_app/models.py`: `Customer`, `Product`, `Order`, `OrderItem`
- `first_app/forms.py`: `ProductForm`, `CustomerForm`, `OrderCreateForm`, `OrderItemFormSet`
- `first_app/views.py`: create, list, update, and delete flows
- `first_app/urls.py`: app routes
- `first_app/templates/first_app/`: product, customer, and order templates
- `first_app/management/commands/seed_sample_data.py`: sample data generator

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Load Sample Data

```powershell
python manage.py seed_sample_data
```

To add more sample orders while reusing the same sample customers and products:

```powershell
python manage.py seed_sample_data --orders 10 --seed 7
```
