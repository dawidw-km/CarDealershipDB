from django.test import TestCase
from ..serializers import CustomerRegistrationSerializer, EmployeeRegistrationSerializer

class PersonRegistrationSerializerTestCase(TestCase):

    def test_customer_registration_serializer(self):
        serializer = CustomerRegistrationSerializer(data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+48123456789",
            "address": "123 Main St, Anytown, USA",
            "date_of_birth": "1990-01-01",
            "password": "Piesek12345"
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

        customer = serializer.save()

        self.assertEqual(customer.user.email, "john.doe@example.com")
        self.assertEqual(customer.phone_number, "+48123456789")
        self.assertTrue(customer.user.check_password("Piesek12345"))


    def test_employee_registration_serializer(self):
        serializer = EmployeeRegistrationSerializer(data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+48123456789",
            "salary": 5000,
            "hire_date": "2020-01-01",
            "password": "Piesek12345"
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

        employee = serializer.save()

        self.assertEqual(employee.user.email, "john.doe@example.com")
        self.assertEqual(employee.phone_number, "+48123456789")
        self.assertEqual(employee.role, "worker")


    def test_customer_registration_serializer_rejects_duplicate_email(self):
        serializer_1 = CustomerRegistrationSerializer(data={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+48123456789",
            "address": "123 Main St",
            "date_of_birth": "1990-01-01",
            "password": "Piesek12345"
        })

        self.assertTrue(serializer_1.is_valid(), serializer_1.errors)

        serializer_1.save()

        serializer_2 = CustomerRegistrationSerializer(data={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+48123456780",
            "address": "Other St",
            "date_of_birth": "1990-01-01",
            "password": "Piesek12345"
        })

        self.assertFalse(serializer_2.is_valid(), serializer_2.errors)
        self.assertIn("email", serializer_2.errors)