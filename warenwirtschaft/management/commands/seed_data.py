import random
import re
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django_seed import Seed
from warenwirtschaft.models import (
    Material, Supplier, Delivery, DeliveryUnit, Unload,
    Recycling, Shipping, ShippingUnit, Customer
)


class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **kwargs):
        seed = Seed.seeder()

        # === Alte Daten löschen vor neuer Datengeneration ===
        Unload.objects.all().delete()
        DeliveryUnit.objects.all().delete()
        Delivery.objects.all().delete()
        Supplier.objects.all().delete()
        Material.objects.all().delete()
        Shipping.objects.all().delete()
        ShippingUnit.objects.all().delete()
        Recycling.objects.all().delete()
        Customer.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Alle Tabellen wurden geleert."))

        # === Hilfsfunktionen für zufällige Email und Notiz ===
        def generate_email(name):
            return f'{re.sub(r"[^a-z]", "", name.lower())}@example.com'

        def generate_note():
            return "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(20, 255)]

        # === Datenquellen ===
        materials_data = [
            "Laptop", "PC", "Dockingstation", "Monitor", "Bildröhren",
            "Kabel", "Gemischte Teile", "Netzteile", "Festplatten",
            "Leiterplatten", "Drucker", "Flat-TV/TFT-Monitore", "Flat-TV", "CRT",
            "Restmüll", "E-Schrott", "DVD/CD", "Batterien", "Schadstoffe"
        ]
        street_names = ["Hauptstraße", "Bahnhofstraße", "Friedrichstraße", "Schillerstraße", "Goethestraße"]
        city_names = ["München", "Germering", "Freising", "Erding", "Starnberg"]
        company_names = [
            "Müller GmbH", "Schmidt GmbH", "Fischer Bau", "Weber Elektro", "Meier GmbH", "Hoffmann IT",
            "Becker Maschinen", "Zimmermann GmbH", "Schneider GmbH", "Bauer Fenster", "Klein und Müller GmbH",
            "Kaiser Bau", "Richter GmbH", "Bergmann Handel", "Wagner und Partner", "Böhm Consulting", "Neumann und Sohn",
            "Graf Technik", "Lang GmbH", "Sauer Möbel", "Peters GmbH", "Jäger GmbH", "Lang Bauunternehmen",
            "Schröder Engineering", "Hansen Möbelbau", "Lenz GmbH", "Bender GmbH", "Böttcher GmbH", "Weber GmbH",
            "Löffler Metallbau", "Kuhn und Schmidt", "Meyer Maschinenbau", "Fuchs und Partner", "Lenz IT",
            "Haas und Söhne", "Wolff und Müller", "Schmitt und Co.", "Stern Elektro GmbH", "Eckert GmbH"
        ]

        # === Materialien ===
        for name in materials_data:
            Material.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Materialien erstellt!"))

        # === Lieferanten ===
        for name in company_names:
            Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'street': f'{random.choice(street_names)} {random.randint(1, 300)}',
                    'postal_code': f'{random.randint(80000, 89999)}',
                    'city': random.choice(city_names),
                    'phone': f'+49{random.randint(100000000, 999999999)}',
                    'email': generate_email(name),
                    'avv_number': random.randint(1000000, 9999999),
                    'note': generate_note(),
                }
            )
        self.stdout.write(self.style.SUCCESS("Lieferanten erstellt!"))

        # === Kunden (Abholer) ===
        for name in company_names:
            Customer.objects.get_or_create(
                name=name,
                defaults={
                    'street': f'{random.choice(street_names)} {random.randint(1, 300)}',
                    'postal_code': f'{random.randint(80000, 89999)}',
                    'city': random.choice(city_names),
                    'phone': f'+49{random.randint(100000000, 999999999)}',
                    'email': generate_email(name),
                    'note': generate_note(),
                }
            )
        self.stdout.write(self.style.SUCCESS("Abholer erstellt!"))

        # === Lieferungen + Versand vorbereiten ===
        suppliers = list(Supplier.objects.all())
        customers = list(Customer.objects.all())

        seed.add_entity(Delivery, 50, {
            'supplier': lambda x: random.choice(suppliers),
            'delivery_receipt': lambda x: f"{random.randint(100000, 999999)}",
            'note': lambda x: generate_note(),
            'created_at': lambda x: timezone.now() - timedelta(days=random.randint(0, 730)),
        })

        seed.add_entity(Shipping, 20, {
            'customer': lambda x: random.choice(customers),
            'certificate': lambda x: f"{random.randint(100000, 999999)}",
            'note': lambda x: generate_note(),
            'created_at': lambda x: timezone.now() - timedelta(days=random.randint(0, 365)),
        })

        inserted = seed.execute()

        # === Übersicht der generierten Einträge ===
        for model, ids in inserted.items():
            self.stdout.write(self.style.SUCCESS(f"{model.__name__}: {len(ids)} Einträge erstellt."))

        # === Liefereinheiten ===
        materials = list(Material.objects.all())
        deliveries = Delivery.objects.all()

        delivery_units = []
        for delivery in deliveries:
            for _ in range(random.randint(1, 4)):
                delivery_units.append(DeliveryUnit(
                    delivery=delivery,
                    material=random.choice(materials),
                    weight=round(random.uniform(100, 500), 2),
                    target=random.choice([1, 2, 3, 4]),
                    status=random.choice([1, 2]),
                    box_type=random.choice([1, 2, 3, 4]),
                    note=generate_note(),
                ))

        DeliveryUnit.objects.bulk_create(delivery_units)
        self.stdout.write(self.style.SUCCESS("Liefereinheiten erstellt!"))

        # === Leerungen (Unload) ===
        unloads = []
        for unit in DeliveryUnit.objects.all():
            for _ in range(random.randint(1, 5)):  # 1–5 Unloads je Einheit
                unloads.append(Unload(
                    delivery_unit=unit,
                    box_type=random.choice([1, 2, 3, 4]),
                    material=random.choice(materials),
                    weight=round(random.uniform(10, 100), 2),
                    target=random.choice([2, 3, 4]),
                    status=random.choice([1, 2]),
                    note=generate_note(),
                ))

        Unload.objects.bulk_create(unloads)
        self.stdout.write(self.style.SUCCESS("Umladung erstellt!"))

        # === Recycling-Einheiten ===
        recyclings = []
        for unit in Unload.objects.all():
            for _ in range(random.randint(1, 5)):
                recyclings.append(Recycling(
                    unload=unit,
                    box_type=random.choice([1, 2, 3, 4]),
                    material=random.choice(materials),
                    weight=round(random.uniform(10, 100), 2),
                    target=random.choice([3, 4]),
                    status=random.choice([1, 2]),
                    note=generate_note(),
                ))

        Recycling.objects.bulk_create(recyclings)
        self.stdout.write(self.style.SUCCESS("Recycling erstellt!"))

        # === Versand-Einheiten ===
        shippings = Shipping.objects.all()
        shipping_units = []

        for shipping in shippings:
            for _ in range(random.randint(1, 4)):
                shipping_units.append(ShippingUnit(
                    shipping=shipping,
                    material=random.choice(materials),
                    weight=round(random.uniform(100, 500), 2),
                    box_type=random.choice([1, 2, 3, 4]),
                    note=generate_note(),
                ))

        ShippingUnit.objects.bulk_create(shipping_units)
        self.stdout.write(self.style.SUCCESS("Versandeinheiten erstellt!"))
