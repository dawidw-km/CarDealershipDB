from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from scheduling.models import ServiceAppointment
from person.models import Customer, Employee
from cars.models import Car
from datetime import date, timedelta

class TestScheduling(TestCase):
    
    def setUp(self):
        
        self.customer_scheduling=Customer.objects.create(
            first_name='Dawid',
            last_name='Niekonieczny',
            email='testscheduling@gmail.com',
            phone_number='530327259',
            address='Moczarów 13',
            date_of_birth=date(2000, 5, 10)
        )

        self.car_scheduling = Car.objects.create(
            brand='Toyota',
            model='Corolla',
            year=2004,
            vin='123456789F2345678',
            vehicel_type='compact car',
            color='blue',
            mileage=40000,
            purchase_price=21500,
        )

        self.service_appointment=ServiceAppointment(
            customer=self.customer_scheduling,
            car=self.car_scheduling,
            appointment_date=timezone.now() + timedelta(days=1),
            service_type=ServiceAppointment.ServiceType.OIL_CHANGE,
            cost=500,
            notes='all good'
        )

    def test_status_service_appointment(self):
        self.assertEqual(self.service_appointment.status, ServiceAppointment.Status.PENDING)

    
    def test_string_representation(self):
        self.assertEqual(str(self.service_appointment), f'{self.service_appointment.customer} - {self.service_appointment.service_type} ({self.service_appointment.appointment_date.date()})')

    def test_invalid_date_service_appointment(self):
        service_appointment_b=ServiceAppointment(
            customer=self.customer_scheduling,
            car=self.car_scheduling,
            appointment_date=timezone.now() - timedelta(days=10),
            service_type=ServiceAppointment.ServiceType.OIL_CHANGE,
            cost=500,
            notes='all good'
        )

        with self.assertRaises(ValidationError) as error:
            service_appointment_b.full_clean()

        self.assertEqual(
            error.exception.message_dict['appointment_date'][0],
            "Appointment date cannot be in the past."
        )

    def test_invalid_notes_service_appointment(self):
        service_appointment_c=ServiceAppointment(
            customer=self.customer_scheduling,
            car=self.car_scheduling,
            appointment_date=timezone.now() + timedelta(days=1),
            service_type=ServiceAppointment.ServiceType.OIL_CHANGE,
            cost=500,
            notes=('a' * 1550)
        )

        with self.assertRaises(ValidationError):
            service_appointment_c.full_clean()
    
    def test_no_service_type_service_appointment(self):
        
        service_appointment_d=ServiceAppointment(
            customer=self.customer_scheduling,
            car=self.car_scheduling,
            appointment_date=timezone.now() + timedelta(days=1),
            cost=500,
            notes='all good'
        )

        with self.assertRaises(ValidationError):
            service_appointment_d.full_clean()

    def test_nullable_cost_service_appointment(self):
        
        service_appointment_e=ServiceAppointment(
            customer=self.customer_scheduling,
            car=self.car_scheduling,
            appointment_date=timezone.now() + timedelta(days=1),
            service_type=ServiceAppointment.ServiceType.OIL_CHANGE,
            notes='all good'
        )
        
        self.assertIsNone(service_appointment_e.cost)
        service_appointment_e.full_clean()