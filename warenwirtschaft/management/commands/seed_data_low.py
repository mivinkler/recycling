"""
Seed-Skript: Testdaten (Fake-Daten) für das Projekt.

Wichtig!:
- Dieses Skript leert relevante Tabellen und erstellt alles neu. Nur in DEV verwenden!
- Die erzeugten Daten sind NICHT für Produktion geeignet.

Erzeugte Daten
--------------
- Eine Liste an Materialien.
- 40 Firmen/Kunden.


Start
------------
# 1) Schema sicherstellen:
        python manage.py makemigrations
        python manage.py migrate

# 2) Paket für Fake-Daten:
        pip install Faker

# 3) Seeds ausführen:
        python manage.py seed_data_low
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker
from warenwirtschaft.models import (
    Material, Customer, Delivery, DeliveryUnit, Unload,
    Recycling, Shipping
)

# deterministische Zufallswerte
random.seed(42)
Faker.seed(42)

# deutschsprachige Daten
fake = Faker("de_DE")


def company_email(name: str) -> str:
    # "Müller GmbH" -> "muellergmbh@example.com"
    base = slugify(name, allow_unicode=False).replace("-", "")
    return f"{base or 'firma'}@example.com"


def random_material_flags() -> dict:
    # Zufällige Booleans für ('delivery','unload','recycling').
    keys = ["delivery", "unload", "recycling"]
    k = random.randint(1, 3)
    chosen = set(random.sample(keys, k))
    return {key: (key in chosen) for key in keys}


class Command(BaseCommand):
    help = "Populate the database with fake data (no django-seed)"

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # DB-Daten löschen (Reihenfolge berücksichtigt FK-Beziehungen)
            Unload.objects.all().delete()
            DeliveryUnit.objects.all().delete()
            Delivery.objects.all().delete()
            Shipping.objects.all().delete()
            Recycling.objects.all().delete()
            Customer.objects.all().delete()
            Material.objects.all().delete()

            self.stdout.write(self.style.SUCCESS("Alle Tabellen wurden geleert."))

            # Materialien inkl. Flags (bulk_create)
            materials_data = [
                "Laptop", "PC", "Dockingstation", "Monitor", "Bildröhren",
                "Kabel", "Gemischte Teile", "Netzteile", "Festplatten",
                "Leiterplatten", "Drucker", "Flat-TV/TFT-Monitore", "Flat-TV", "CRT",
                "Restmüll", "E-Schrott", "DVD/CD", "Batterien", "Schadstoffe"
            ]
            materials = []
            for name in materials_data:
                flags = random_material_flags()
                materials.append(Material(name=name, **flags))
            Material.objects.bulk_create(materials)

            # Eindeutige Firmennamen + Kunden (bulk_create)
            company_names = [fake.unique.company() for _ in range(40)]
            customers = [
                Customer(
                    name=name,
                    street=fake.street_address(),
                    postal_code=fake.postcode(),
                    city=fake.city(),
                    phone=fake.phone_number(),
                    email=company_email(name),
                    avv_number=fake.random_int(min=1000000, max=9999999),
                    note=fake.text(max_nb_chars=random.randint(20, 255)),
                )
                for name in company_names
            ]
            Customer.objects.bulk_create(customers)

            # Abschluss: kleine Statistiken
            self.stdout.write(self.style.SUCCESS(f"Materialien erstellt: {Material.objects.count()}"))
            self.stdout.write(self.style.SUCCESS(f"Kunden erstellt: {Customer.objects.count()}"))