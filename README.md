# Sales Tracker Database (Django)

A Django practice project focused on building a simple sales tracker database with CRUD operations.

## Current Scope

- Product create and list in one page (`/products/`)
- Product update (`/products/<id>/edit/`)
- Product delete via POST (`/products/<id>/delete/`)
- SQLite database (`db.sqlite3`)

## Tech Stack

- Python
- Django 6
- SQLite

## Project Structure

- `first_app/models.py`: `Customer`, `Product`, `Order`, `OrderItem`
- `first_app/forms.py`: `ProductForm`
- `first_app/views.py`: list/create, update, delete views
- `first_app/urls.py`: app routes
- `first_app/templates/first_app/products.html`: UI template

## Run Locally

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
