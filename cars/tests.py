from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from .models import Cars

class CarTestCase(TestCase):
    def setUp(self):
       self.car_a = Cars.objects.create(
            brand='Toyota',
            model='Corolla',
            year=2004,
            vin='123456789F2345678',
            vehicel_type='compact car',
            color='blue',
            mileage=40000,
            purchase_price=21500,
        )
    
    def test_string_representation(self):
        self.assertEqual(str(self.car_a), 'Toyota Corolla (2004)')

    def test_car_status(self):
        self.assertEqual(self.car_a.status, 'available')
        
    def test_valid_vin_number(self):
        self.car_a.full_clean()
    
    def test_uniqueness_vin_error(self):
        with self.assertRaises(IntegrityError):
            Cars.objects.create(
                    brand='Toyota',
                    model='Wroom',
                    vehicel_type='compact car',
                    color='yellow',
                    year=2000,
                    vin='123456789F2345678',
                    mileage=2000,
                    )


    def test_invalid_vin_number(self):
        car_2 = Cars(
                brand='Mercedes',
                model='Benz',
                vehicel_type='compact car',
                color='black',
                year=2000,
                vin='QQQQQQQ123456789Q',
                mileage=200000,
                )

        with self.assertRaises(ValidationError):
            car_2.full_clean()

    def test_description_too_long(self):
        car_3 = Cars(
                brand='BMW',
                model='E200',
                year=2010,
                vehicel_type='SUV',
                color='white',
                vin='12345678901234567',
                mileage=253323,
                description=('a' * 600)
                )
        
        with self.assertRaises(ValidationError):
            car_3.full_clean()

    def test_year_too_early(self):
        car_4 = Cars(
                brand='Mercedes',
                model='Benz',
                vehicel_type='Sports car',
                color='red',
                year=1880,
                vin='12345678901234567',
                mileage=2000,
                )

        with self.assertRaises(ValidationError):
            car_4.full_clean()

    def test_year_too_late(self):
        car_5 = Cars(
                brand='Mercedes',
                model='Benz',
                vehicel_type='Racing car',
                color='orange',
                year=5000,
                vin='12345678901234567',
                mileage=20000,
                )
        
        with self.assertRaises(ValidationError):
            car_5.full_clean()

    def test_mileage_value_too_high(self):
        car_6 = Cars(
                brand='Mercedes',
                model='Benz',
                vehicel_type='Racing car',
                color='silver',
                year=2021,
                vin='12345678901234567',
                mileage=20000000,
                )

        with self.assertRaises(ValidationError):
            car_6.full_clean()
