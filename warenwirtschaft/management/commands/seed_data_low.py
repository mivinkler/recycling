import random
import re
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django_seed import Seed
from warenwirtschaft.models import (
    Material, Supplier, Delivery, DeliveryUnit, Unload,
    Recycling, Shipping, Customer
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
