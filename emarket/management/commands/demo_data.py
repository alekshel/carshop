import random

from django.core.management.base import BaseCommand
from faker import Faker

from emarket.models import Client, CarType, Car, Dealership

fake = Faker("uk")

CAR_TYPES = (
    {"name": "Пассат", "brand": "Volkswagen", "dealership": "Київ АвтоСервіс"},
    {"name": "Гольф", "brand": "Volkswagen", "dealership": "Дніпро АвтоСервіс"},
    {"name": "Меган", "brand": "Renault", "dealership": "Київ АвтоСервіс"},
    {"name": "Кєнгу", "brand": "Renault", "dealership": "Київ АвтоСервіс"},
    {"name": "Лагуна", "brand": "Renault", "dealership": "Дніпро АвтоСервіс"},
)


class Command(BaseCommand):
    help = "Add subjects"

    def handle(self, *args, **options):
        Client.objects.all().delete()
        Car.objects.all().delete()
        CarType.objects.all().delete()
        Dealership.objects.all().delete()

        Client.objects.create(
            name=fake.name(),
            email=fake.email(),
            phone="+38050" + str(random.randint(1000000, 9999999)),
        )

        for car_type in CAR_TYPES:
            type_id = CarType.objects.create(
                name=car_type["name"],
                brand=car_type["brand"],
                price=random.randint(10000, 30000),
            )

            for i in range(random.randint(5, 15)):
                Car.objects.create(
                    car_type=type_id,
                    color=fake.color(),
                    year=random.randint(2005, 2023),
                )

            obj, created = Dealership.objects.get_or_create(name=car_type["dealership"])
            obj.available_car_types.add(type_id)

        self.stdout.write(self.style.SUCCESS("Successfully added"))
