from django.core.management.base import BaseCommand
from warenwirtschaft.models import Supplier, Material, Delivery, DeliveryUnit
import random
from datetime import date, timedelta
from django_seed import Seed
import re

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        seed = Seed.seeder()

        materials_data = [
            "Notebook", "PC", "Dockingstation", "Monitor", "Mini-PCs",
            "Kabel", "Gemischte Teile", "HDD", "SSD", "Prozessoren", 
            "Grafikkarten", "Festplatten", "Netzteile", "Laufwerke",
            "Server", "Drucker", "Bildröhren", "CU-Abschirmkabel"
            "Beamer", "Fernseher", "DVD/CD", "Tablets", "Ladekabel und Adapter", 
            "Spülmaschine", "Kaffeemaschine", "Waschmaschine", 
            "Waschtrockner", "Kühlschränke", "Klimageräte",
        ]

        def create_materials():
            for material_name in materials_data:
                Material.objects.get_or_create(name=material_name)

        create_materials()
        self.stdout.write(self.style.SUCCESS("Materials have been created."))

        # Lieferant
        street_names = [
            "Hauptstraße", "Bahnhofstraße", "Dorfstraße", "Friedrichstraße", "Schillerstraße", "Goethestraße", 
            "Bismarckstraße", "Lindenstraße", "Poststraße", "Königstraße", "Karlstraße", "Wilhelmstraße", 
            "Maxstraße", "Steinstraße", "Am Markt"
        ]

        def random_street_name():
            street = random.choice(street_names)
            house_number = random.randint(1, 300)
            return f'{street} {house_number}'

        company_names = [
            "Müller GmbH", "Schmidt GmbH", "Fischer Bau", "Weber Elektro", "Meier GmbH", "Hoffmann IT", 
            "Becker Maschinen", "Zimmermann GmbH", "Schneider GmbH", "Bauer Fenster", "Klein und Müller GmbH", 
            "Kaiser Bau", "Richter GmbH", "Bergmann Handel", "Wagner und Partner", "Böhm Consulting", "Neumann und Sohn", 
            "Graf Technik", "Lang GmbH", "Sauer Möbel", "Peters GmbH", "Jäger GmbH", "Lang Bauunternehmen", 
            "Schröder Engineering", "Hansen Möbelbau", "Lenz GmbH", "Bender GmbH", "Böttcher GmbH", "Weber GmbH", 
            "Löffler Metallbau", "Kuhn und Schmidt", "Meyer Maschinenbau", "Fuchs und Partner", "Lenz IT", 
            "Haas und Söhne", "Wolff und Müller", "Schmitt und Co.", "Stern Elektro GmbH", "Eckert GmbH"
        ]

        city_names = [
            "München", "Germering", "Freising", "Erding", "Deggendorf", "Unterschleißheim", "Unterhaching", 
            "Starnberg", "Haar", "Puchheim", "Freising"
        ]

        # Löschen der Tabelle supplier vor der Datengenerierung
        Supplier.objects.all().delete()

        # Generierung von Lieferanten mit ID Prüfung
        for name in company_names:
            if not Supplier.objects.filter(name=name).exists():
                seed.add_entity(Supplier, 1, {
                    'name': lambda x, name=name: name,
                    'street': lambda x: random_street_name(),
                    'postal_code': lambda x: f'{random.randint(80000, 89999)}',
                    'city': lambda x: random.choice(city_names),
                    'phone': lambda x: f'+{random.randint(1000000000, 9999999999)}',
                    'email': lambda x, name=name: f'{re.sub(r"[^a-z]", "", name.replace(" ", "").lower())}@example.com',
                    'avv_number': lambda x: random.randint(100000000, 999999999),
                })

        materials = Material.objects.all()
        suppliers = Supplier.objects.all()

        seed.add_entity(Delivery, 1000, {
            'supplier': lambda x: random.choice(list(suppliers)) if suppliers.exists() else None,
            'weight': lambda x: round(random.uniform(100, 1000), 2),
            'note': lambda x: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."[:random.randint(100, 255)],
            'delivery_receipt': lambda x: random.choice([None, f"Receipt-{random.randint(1000, 9999)}"]),
            'created_at': lambda x: date.today() - timedelta(days=random.randint(0, 365)),
        })

        inserted_pks = seed.execute()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(inserted_pks)} entries in Delivery.'))

        # Delivery units
        deliveries = Delivery.objects.all()

        # Datenerfassung für DeliveryUnits
        delivery_units_data = []
        for delivery in deliveries:
            num_units = delivery.units or random.randint(1, 5)
            for _ in range(num_units):  # Erstellung von mehreren Datensätzen für jede Lieferung
                delivery_units_data.append({
                    'delivery_id': delivery.id,
                    'material_id': random.choice(materials).id,
                    'weight': round(random.uniform(100, 1000), 2),
                    'status': random.choice([1, 2, 3]),
                    'delivery_type': random.choice([1, 2, 3, 4]),
                    'note': "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(100, 255)],
                    'delivery_receipt': random.choice([None, f"Receipt-{random.randint(1000, 9999)}"]),
                })

        # Nach dem Sammelung von Daten werden diese zur Datenbank hinzugefügt
        if delivery_units_data:
            DeliveryUnit.objects.bulk_create([DeliveryUnit(**data) for data in delivery_units_data])
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(delivery_units_data)} entries in DeliveryUnits.'))
        else:
            self.stdout.write(self.style.WARNING("No delivery units to create."))
