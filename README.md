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
| `/api-auth/`    | DRF browsable API session login            |




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


| URL                         | Description                    |
| --------------------------- | ------------------------------ |
| `/customer/profile/`        | Customer dashboard             |
| `/customer/profile/update/` | Update profile                 |
| `/me/cars/`                 | View own car listings          |
| `/customer/car/register/`   | Register a new car             |
| `/me/cars/update/<id>/`     | Update a car listing           |
| `/buyer/sales/`             | Sales where you are the buyer  |
| `/owner/sales/`             | Sales where you are the seller |
| `/user/change-password/`    | Change password                |


**Employee pages**


| URL                                   | Description                          |
| ------------------------------------- | ------------------------------------ |
| `/employee/profile/`                  | Employee dashboard                   |
| `/employee/car/moderation/list/`      | Cars pending moderation              |
| `/employee/deleted/cars/`             | Soft-deleted cars                    |
| `/customer/list/`                     | Customer list                        |
| `/staff/sales/`                       | All sales transactions               |
| `/employee/list/`                     | Employee list (admin only)           |
| `/employee/admin/employees/register/` | Register a new employee (admin only) |


Use the demo accounts above to explore each role. Log out via `/logout/`.

## User roles

The system has two main user types: **Customer** and **Employee**. Employees are further split into **worker** and **admin** roles.

### Customer

- Register an account
- View and update own profile
- Register, view, update, and soft-delete own car listings
- Browse approved car listings
- Reserve or purchase cars
- View own sales as buyer or seller
- Change password



### Employee (worker)

- View own profile
- Approve or reject customer car listings
- Soft-delete cars
- View rejected, soft-deleted, and pending cars
- View customer list and all sales transactions
- Change password



### Employee (admin)

Everything a worker can do, plus:

- Register new employees
- View employee list
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
scheduling/        # service appointments (work in progress)
```



## Roadmap

- [x] Customer and employee management
- [x] Car listings with employee moderation
- [x] Car reservation and sales flow
- [x] REST API with Swagger documentation
- [x] Django template frontend
- [ ] Scheduling module (still in development)



## Running tests

```bash
docker compose exec web python manage.py test
```



## About

Personal portfolio project built to practice Django, REST API design, role-based access control, and domain validation. Core features are complete. Scheduling is still in development.