import random
import re
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django_seed import Seed
from warenwirtschaft.models import Material, Supplier, Delivery, DeliveryUnit, Unload


class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **kwargs):
        seed = Seed.seeder()

        # === Alte Daten löschen vor der neuen Datengeneration ===
        Unload.objects.all().delete()
        DeliveryUnit.objects.all().delete()
        Delivery.objects.all().delete()
        Supplier.objects.all().delete()
        Material.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Alle Tabellen wurden geleert."))

        # === Materialien ===
        materials_data = [
            "Laptop", "PC", "Dockingstation", "Monitor", "Bildröhren",
            "Kabel", "Gemischte Teile", "Netzteile", "Festplatten",
            "Leiterplatten", "Drucker", "Flat-TV/TFT-Monitore", "Flat-TV", "CRT",
            "Restmüll", "E-Schrott", "DVD/CD", "Batterien", "Schadstoffe"
        ]

        for name in materials_data:
            Material.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Materialien erstellt!"))

        # === Lieferanten ===
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

        for name in company_names:
            email = f'{re.sub(r"[^a-z]", "", name.lower())}@example.com'
            Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'street': f'{random.choice(street_names)} {random.randint(1, 300)}',
                    'postal_code': f'{random.randint(80000, 89999)}',
                    'city': random.choice(city_names),
                    'phone': f'+49{random.randint(100000000, 999999999)}',
                    'email': email,
                    'avv_number': random.randint(1000000, 9999999),
                    'note': "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(20, 255)],
                }
            )
        self.stdout.write(self.style.SUCCESS("Lieferanten erstellt!"))

        # === Lieferungen ===
        suppliers = list(Supplier.objects.all())
        now = timezone.now()

        seed.add_entity(Delivery, 50, {
            'supplier': lambda x: random.choice(suppliers),
            'delivery_receipt': lambda x: f"{random.randint(100000, 999999)}",
            'created_at': lambda x: now - timedelta(days=random.randint(0, 730)),
            'note': "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(20, 255)],
        })

        inserted = seed.execute()
        self.stdout.write(self.style.SUCCESS(f"Lieferungen erstellt!"))

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
                    status=random.choice([1, 2]),
                    delivery_type=random.choice([1, 2, 3, 4]),
                    note="Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(20, 255)],
                ))

        DeliveryUnit.objects.bulk_create(delivery_units)
        self.stdout.write(self.style.SUCCESS(f"Liefereinheiten erstellt!"))

        # === Leerungen (Unload) ===
        unloads = []
        for unit in DeliveryUnit.objects.all():
            for _ in range(random.randint(1, 3)):  # 1–3 Unload für einen Delivery_unit
                unloads.append(Unload(
                    delivery_unit=unit,
                    unload_type=random.choice([1, 2, 3, 4]),
                    material=random.choice(materials),
                    weight=round(random.uniform(10, 100), 2),
                    purpose=random.choice([1, 2, 3]),
                    status=random.choice([1, 2]),
                    note="Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(20, 255)],
                ))

        Unload.objects.bulk_create(unloads)
        self.stdout.write(self.style.SUCCESS(f"Leerungen erstellt!"))