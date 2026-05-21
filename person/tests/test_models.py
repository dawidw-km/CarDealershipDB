from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Customer, Employee

User = get_user_model()


class CustomerTestCase(TestCase):

    def create_user(self, email):
        return User.objects.create_user(
            username=email,
            email=email,
            password='testpassword'
        )
    

    def create_customer(self, email):
        user = self.create_user(email)

        return Customer.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            address="Warszawska 12",
            date_of_birth=date(1990, 1, 1)
        )

    def create_employee(self, email):
        user = self.create_user(email)

        return Employee.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1),
            employment_status=Employee.EmploymentStatus.ACTIVE
        )


    def create_admin_employee(self, email):
        user = self.create_user(email)

        return Employee.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1),
            employment_status=Employee.EmploymentStatus.ACTIVE
        )


    # Customer tests

    def test_customer_creation_is_valid(self):

        self.customer_1 = self.create_customer("testuser1@gmail.com")

        self.customer_1.full_clean()

    def test_first_name_cannot_contain_special_characters(self):

        self.customer_2 = self.create_customer("testuser2@gmail.com")

        self.customer_2.first_name = "Dawid!"

        with self.assertRaises(ValidationError) as error:
            self.customer_2.full_clean()

        self.assertEqual(
            error.exception.message_dict["first_name"][0],
            "Name can contain only letters."
        )


    def test_last_name_cannot_contain_special_characters(self):

        self.customer_3 = self.create_customer("testuser3@gmail.com")
        self.customer_3.last_name = "Reacher!"

        with self.assertRaises(ValidationError):
            self.customer_3.full_clean()


    def test_email_is_required(self):

        self.customer_4 = self.create_customer("testuser4@gmail.com")
        self.customer_4.email = None

        with self.assertRaises(ValidationError):
            self.customer_4.full_clean()


    def test_invalid_email(self):

        self.customer_5 = self.create_customer("testuser3@gmail.com")

        self.customer_5.email = "wrong-email"

        with self.assertRaises(ValidationError):
            self.customer_5.full_clean()


    def test_address_is_required(self):

        self.customer_6 = self.create_customer("testuser6@gmail.com")
        self.customer_6.address = None

        with self.assertRaises(ValidationError):
            self.customer_6.full_clean()

    
    def test_birth_date_is_required(self):

        self.customer_7 = self.create_customer("testuser7@gmail.com")
        self.customer_7.date_of_birth = None

        with self.assertRaises(ValidationError):
            self.customer_7.full_clean()


    def test_phone_number_wrong_region(self):

        self.customer_9 = self.create_customer("testuser9@gmail.com")
        self.customer_9.phone_number = "+47123456789"

        with self.assertRaises(ValidationError):
            self.customer_9.full_clean()


    def test_duplicated_email(self):

        self.create_customer("testuser4@gmail.com")

        duplicated_customer = self.create_customer("another@gmail.com")
        duplicated_customer.email = "testuser4@gmail.com"

        with self.assertRaises(ValidationError):
            duplicated_customer.full_clean()


    def test_phone_number_is_required(self):

        self.customer_10 = self.create_customer("testuser5@gmail.com")
        self.customer_10.phone_number = None

        with self.assertRaises(ValidationError):
            self.customer_10.full_clean()


    def test_birth_date_cannot_be_in_future(self):

        self.customer_11 = self.create_customer("testuser6@gmail.com")
        self.customer_11.date_of_birth = date(2100, 1, 1)

        with self.assertRaises(ValidationError):
            self.customer_11.full_clean()


    def test_customer_must_be_adult(self):

        self.customer_12 = self.create_customer("testuser7@gmail.com")
        self.customer_12.date_of_birth = date(date.today().year - 17, 1, 1)

        with self.assertRaises(ValidationError):
            self.customer_12.full_clean()
    

    def test_address_too_short(self):

        self.customer_13 = self.create_customer("testuser8@gmail.com")
        self.customer_13.address = "Short"

        with self.assertRaises(ValidationError):
            self.customer_13.full_clean()

    # Employee tests
    
    def test_employee_creation(self):

        self.employee_1 = self.create_employee("testemployee1@gmail.com")
        self.employee_1.full_clean()

        self.assertEqual(self.employee_1.first_name, "Jack")
        self.assertEqual(self.employee_1.last_name, "Reacher")
        self.assertEqual(self.employee_1.email, "testemployee1@gmail.com")
        self.assertEqual(self.employee_1.phone_number, "+48123456789")
        self.assertEqual(self.employee_1.role, Employee.EmployeeRole.WORKER)
        self.assertEqual(self.employee_1.salary, 5000)
        self.assertEqual(self.employee_1.hire_date, date(2020, 1, 1))
        self.assertEqual(self.employee_1.employment_status, Employee.EmploymentStatus.ACTIVE)

    def test_employee_creation_with_invalid_role(self):

        self.employee_2 = self.create_employee("testemployee2@gmail.com")
        self.employee_2.role = "invalid"

        with self.assertRaises(ValidationError):
            self.employee_2.full_clean()

    def test_employee_creation_with_invalid_salary_negative(self):

        self.employee_3 = self.create_employee("testemployee3@gmail.com")
        self.employee_3.salary = -1000

        with self.assertRaises(ValidationError):
            self.employee_3.full_clean()

    def test_employee_creation_with_invalid_employment_status(self):

        self.employee_5 = self.create_employee("testemployee5@gmail.com")
        self.employee_5.employment_status = "invalid"

        with self.assertRaises(ValidationError):
            self.employee_5.full_clean()

    def test_admin_employee_creation(self):

        self.admin_employee_1 = self.create_admin_employee("testadminemployee1@gmail.com")
        self.admin_employee_1.full_clean()

        self.assertEqual(self.admin_employee_1.first_name, "Jack")
        self.assertEqual(self.admin_employee_1.last_name, "Reacher")
        self.assertEqual(self.admin_employee_1.email, "testadminemployee1@gmail.com")
        self.assertEqual(self.admin_employee_1.phone_number, "+48123456789")
        self.assertEqual(self.admin_employee_1.role, Employee.EmployeeRole.ADMIN)
        self.assertEqual(self.admin_employee_1.salary, 5000)
        self.assertEqual(self.admin_employee_1.hire_date, date(2020, 1, 1))

    def test_salary_is_required(self):

        self.employee_6 = self.create_employee("testemployee6@gmail.com")
        self.employee_6.salary = None

        with self.assertRaises(ValidationError):
            self.employee_6.full_clean()

    def test_hire_date_is_required(self):

        self.employee_7 = self.create_employee("testemployee7@gmail.com")
        self.employee_7.hire_date = None

        with self.assertRaises(ValidationError):
            self.employee_7.full_clean()

    def test_hire_date_cannot_be_in_future(self):

        self.employee_8 = self.create_employee("testemployee8@gmail.com")
        self.employee_8.hire_date = date(2100, 1, 1)

        with self.assertRaises(ValidationError):
            self.employee_8.full_clean()

    def test_employment_status_is_required(self):

        self.employee_9 = self.create_employee("testemployee9@gmail.com")
        self.employee_9.employment_status = None

        with self.assertRaises(ValidationError):
            self.employee_9.full_clean()

    def test_layoff_and_active_employment_status_cannot_be_set_together(self):

        self.employee_10 = self.create_employee("testemployee10@gmail.com")
        self.employee_10.employment_status = Employee.EmploymentStatus.ACTIVE
        self.employee_10.layoff_date = date(2024, 1, 1)

        with self.assertRaises(ValidationError):
            self.employee_10.full_clean()

    def test_no_layoff_and_inactive_employment_status_cannot_be_set_together(self):

        self.employee_11 = self.create_employee("testemployee11@gmail.com")
        self.employee_11.employment_status = Employee.EmploymentStatus.INACTIVE
        self.employee_11.layoff_date = None

        with self.assertRaises(ValidationError):
            self.employee_11.full_clean()


    def test_inactive_employee_with_layoff_date_is_valid(self):

        self.employee_12 = self.create_employee("testemployee12@gmail.com")
        self.employee_12.employment_status = Employee.EmploymentStatus.INACTIVE
        self.employee_12.layoff_date = date(2024, 1, 1)

        self.employee_12.full_clean()

        self.assertEqual(self.employee_12.employment_status, Employee.EmploymentStatus.INACTIVE)
        self.assertEqual(self.employee_12.layoff_date, date(2024, 1, 1))

    
    def test_active_employee_without_layoff_date_is_valid(self):

        self.employee_13 = self.create_employee("testemployee13@gmail.com")
        self.employee_13.employment_status = Employee.EmploymentStatus.ACTIVE
        self.employee_13.layoff_date = None

        self.employee_13.full_clean()

        self.assertEqual(self.employee_13.employment_status, Employee.EmploymentStatus.ACTIVE)
        self.assertEqual(self.employee_13.layoff_date, None)
        
    def test_layoff_date_cannot_be_in_future(self):

        self.employee_14 = self.create_employee("testemployee14@gmail.com")
        self.employee_14.employment_status = Employee.EmploymentStatus.INACTIVE
        self.employee_14.layoff_date = date(2100, 1, 1)

        with self.assertRaises(ValidationError):
            self.employee_14.full_clean()


    def test_default_role_is_worker(self):

        email = "testemployee16@gmail.com"
        user = self.create_user(email)

        employee = Employee.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            salary=5000,
            hire_date=date(2020, 1, 1),
        )

        employee.full_clean()

        self.assertEqual(employee.role, Employee.EmployeeRole.WORKER)


    def test_default_employment_status_is_active(self):
        email = "testemployee16@gmail.com"
        user = self.create_user(email)

        employee = Employee.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1),
        )

        employee.full_clean()

        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.ACTIVE)


    def test_customer_cannot_be_created_if_user_has_employee_profile(self):

        self.employee_1 = self.create_employee("testemployee1@gmail.com")

        customer = Customer(
            user=self.employee_1.user,
            first_name="Jack",
            last_name="Reacher",
            email="testemployee1@gmail.com",
            phone_number="+48123456789",
            address="Warszawska 12",
            date_of_birth=date(1990, 1, 1)
        )

        with self.assertRaises(ValidationError):
            customer.full_clean()


    def test_employee_cannot_be_created_if_user_has_customer_profile(self):

        self.customer_1 = self.create_customer("testcustomer1@gmail.com")

        employee = Employee(
            user=self.customer_1.user,
            first_name="Jack",
            last_name="Reacher",
            email="testcustomer1@gmail.com",
            phone_number="+48123456789",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1),
            employment_status=Employee.EmploymentStatus.ACTIVE
        )

        with self.assertRaises(ValidationError):
            employee.full_clean()