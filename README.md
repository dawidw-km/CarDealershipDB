# Car Dealership DB

A dealership management system for listing, moderating, and selling new and used cars. Built with Django, Django REST Framework, and PostgreSQL.

## Tech stack

- **Backend:** Django 4.2, Django REST Framework
- **Auth:** JWT (Simple JWT), role-based permissions
- **Database:** PostgreSQL 16
- **API docs:** drf-spectacular (OpenAPI / Swagger)
- **Infrastructure:** Docker Compose

## Requirements

- Docker

## Quick start

```bash
git clone https://github.com/dawidw-km/CarDealershipDB.git
cd CarDealershipDB

cp .env_example .env

docker compose up --build
```

The application runs at [http://localhost:8000](http://localhost:8000).

### Seed demo data

In a separate terminal, after the containers are up:

```bash
docker compose exec web python manage.py seed_superuser
docker compose exec web python manage.py seed_demo_data
```

### Demo accounts


| Role              | Email                   | Password      |
| ----------------- | ----------------------- | ------------- |
| Superuser         | `admin@admin.com`       | `Admin123!`   |
| Customer          | `customer@customer.com` | `Customer123` |
| Employee (worker) | `worker@employee.com`   | `Worker123`   |
| Employee (admin)  | `admin@employee.com`    | `Admin123`    |




## Entry points


| URL             | Description                                |
| --------------- | ------------------------------------------ |
| `/docs/`        | Swagger UI (interactive API documentation) |
| `/docs/schema/` | OpenAPI schema                             |
| `/admin/`       | Django admin panel                         |
| `/api/api-auth/` | DRF browsable API session login            |




## Web UI (Django templates)

Besides the REST API, the project includes a basic server-rendered UI built with Django templates. It mirrors the main workflows and is useful for manual testing without API clients.

**Start here:**


| URL                        | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `/login/form/`             | Log in as customer or employee                   |
| `/register/customer/form/` | Register a new customer account                  |
| `/public/cars/`            | Browse approved car listings (no login required) |


After logging in, users are redirected to their profile page (`/customer/profile/` or `/employee/profile/`), which links to role-specific pages.

**Customer pages**


| URL                             | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `/customer/profile/`            | Customer dashboard                                      |
| `/customer/profile/update/`     | Update profile                                          |
| `/me/cars/`                     | View own car listings (soft-delete own cars via button) |
| `/customer/car/register/`       | Register a new car                                      |
| `/me/cars/update/<id>/`         | Update a car listing                                    |
| `/customer/car/reservation/<id>/` | Reserve a car (via button on `/public/cars/`)         |
| `/buyer/car/reservation/list/`  | Cars you have reserved                                  |
| `/owner/car/reservation/list/`  | Your cars that someone has reserved                     |
| `/customer/sale/register/<id>/` | Purchase a car (template UI)                            |
| `/buyer/sales/`                 | Sales where you are the buyer                           |
| `/owner/sales/`                 | Sales where you are the seller                          |
| `/user/change-password/`        | Change password                                         |


**Employee pages**


| URL                                   | Description                                         |
| ------------------------------------- | --------------------------------------------------- |
| `/employee/profile/`                  | Employee dashboard                                  |
| `/employee/car/moderation/list/`      | Cars pending moderation                             |
| `/staff/car/reservation/list/`        | All reserved cars (employee or superuser)           |
| `/employee/deleted/cars/`             | Soft-deleted cars                                   |
| `/customer/list/`                     | Customer list                                       |
| `/staff/sales/`                       | All sales transactions                              |
| `/employee/list/`                     | Employee list (admin only)                          |
| `/employee/admin/employees/register/` | Register a new employee (admin only)                |
| `/public/cars/`                       | Soft-delete cars (admin employee or superuser only) |


Use the demo accounts above to explore each role. Log out via `/logout/`.

## User roles

The system has two main user types: **Customer** and **Employee**. Employees are further split into **worker** and **admin** roles.

### Customer

- Register an account
- View and update own profile
- Register, view, update, and soft-delete own car listings
- Browse approved car listings
- Reserve cars via API (`PATCH /api/cars/<id>/purchase-status/reserved/`) — template UI not implemented yet
- Purchase cars via API or template UI (`/customer/sale/register/<id>/`)
- View own sales as buyer or seller
- Change password



### Employee (worker)

- View own profile
- Approve or reject customer car listings
- View rejected, soft-deleted, and pending cars
- View customer list and all sales transactions
- Cannot soft-delete cars
- Change password



### Employee (admin)

Everything a worker can do, plus:

- Register new employees
- View employee list
- Soft-delete any car listing (not reserved or sold) via `/public/cars/`
- Update employee profiles
- Change employee employment status (active / inactive)



### Superuser

A superuser is required to bootstrap the first admin employee. Superusers can access the Django admin panel and have elevated access across the system.

## Authentication

- `POST /api/customer/token/` — customer JWT login
- `POST /api/employee/token/` — employee JWT login
- `POST /api/employee/token/refresh/` — JWT token refresh
- `PATCH /api/change-password/` — change password (authenticated users)



## Project structure

```
CarDealershipDB/   # project settings, API routing, docs
person/            # customers, employees, authentication
cars/              # car listings, moderation, soft delete
sales/             # purchase transactions
```


## Running tests

```bash
docker compose exec web python manage.py test
```



## About

Personal portfolio project built to practice Django, REST API design, role-based access control, and domain validation. Core features are complete.