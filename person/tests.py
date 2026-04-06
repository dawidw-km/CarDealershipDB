from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Customers

class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer_1=Customers(
            first_name='Dawid',
            last_name='Niekonieczny',
            email='testcase@gmail.com',
            phone_number='535327259',
            address='Moczarów 13',
            date_of_birth=date(2000, 5, 10)
        )

        self.customer_1.full_clean()

    def test_first_name_cannot_contain_special_characters(self):
        self.customer_2=Customers(
            first_name='Dawid!',
            last_name='Niekonieczny',
            email='test1@gmail.com',
            phone_number='535497259',
            address='Moczarów 13',
            date_of_birth=date(2000, 5, 10)
        )

        with self.assertRaises(ValidationError) as error:
            self.customer_2.full_clean()

        self.assertEqual(
            error.exception.message_dict["first_name"][0],
            "Name can contain only letters."
        )

    def test_invalid_email(self):
        self.customer_3=Customers(
            first_name='Robert',
            last_name='Janczarski',
            email='wrong-email',
            phone_number='555555444',
            address='Szczecin ul.Górska 12',
            date_of_birth=date(1980, 10, 4)
        )

        with self.assertRaises(ValidationError):
            self.customer_3.full_clean()


    def test_duplicated_email(self):
        self.customer_4=Customers.objects.create(
            first_name='Mike',
            last_name='Spayson',
            email='mikespayson@gmail.com',
            phone_number='645432675',
            address='Wrocław ul.Grabicka 13',
            date_of_birth=date(2001, 2, 3)
        )

        self.customer_5=Customers(
            first_name='Pike',
            last_name='Spayson',
            email='mikespayson@gmail.com',
            phone_number='645432625',
            address='Wrocław ul.Grabicka 13',
            date_of_birth=date(2001, 3, 3)
        )

        with self.assertRaises(ValidationError):
            self.customer_5.full_clean()

    
    def test_phone_number_is_required(self):
        self.customer_6=Customers(
            first_name='Michał',
            last_name='Woźniak',
            email='michalwolzniak12@gmail.com',
            address="Bydgoszcz os.1000lecia 12",
            date_of_birth=date(1999, 10, 10)
        )

        with self.assertRaises(ValidationError):
            self.customer_6.full_clean()

    
    def test_birth_date_cannot_be_in_future(self):
        self.customer_7=Customers(
            first_name='Jan',
            last_name='Nowak',
            email='jan.nowak@gmail.com',
            phone_number='535397257',
            address='Warszawa ul. Terasowa 12',
            date_of_birth=date(2100, 1, 1)
        )

        with self.assertRaises(ValidationError) as error:
            self.customer_7.full_clean()

        self.assertEqual(
            error.exception.message_dict["date_of_birth"][0],
            "Date cannot be in the future."
        )

    def test_customer_must_be_adult(self):
        self.customer_8=Customers(
            first_name='Jan',
            last_name='Nowak',
            email='jan.nowak2@gmail.com',
            phone_number='512397259',
            address='Warszawa ul. Terasowa 12',
            date_of_birth=date(date.today().year - 17, 1, 1)
        )

        with self.assertRaises(ValidationError) as error:
            self.customer_8.full_clean()

        self.assertEqual(
            error.exception.message_dict["date_of_birth"][0],
            "User has to be at least 18 years old."
        )
    
    
    def test_address_too_short(self):
        self.customer_9=Customers(
            first_name='Jan',
            last_name='Kowalski',
            email='janek.kowalski@gmail.com',
            phone_number='512512512',
            address='Short',
            date_of_birth=date(2000, 10, 10)
        )

        with self.assertRaises(ValidationError):
            self.customer_9.full_clean()
