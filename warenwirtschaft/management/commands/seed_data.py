import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from django.utils import timezone
from datetime import timedelta
from random import randint
from warenwirtschaft.models import Material, Supplier, Delivery, DeliveryUnit
import re

class Command(BaseCommand):
    help = 'Populate the database with fake data'

    def handle(self, *args, **kwargs):
        # Инициализация сеедера
        seed = Seed.seeder()

        # Генерация материалов
        materials_data = [
            "Notebook", "PC", "Dockingstation", "Monitor", "Mini-PCs",
            "Kabel", "Gemischte Teile", "HDD", "SSD", "Prozessoren", 
            "Grafikkarten", "Festplatten", "Netzteile", "Laufwerke",
            "Server", "Drucker", "Bildröhren", "CU-Abschirmkabel",
            "Beamer", "Fernseher", "DVD/CD", "Tablets", "Ladekabel und Adapter", 
            "Spülmaschine", "Kaffeemaschine", "Waschmaschine", 
            "Waschtrockner", "Kühlschränke", "Klimageräte",
        ]

        def create_materials():
            for material_name in materials_data:
                Material.objects.get_or_create(name=material_name)

        create_materials()
        self.stdout.write(self.style.SUCCESS("Materials have been created."))

        # Генерация поставщиков
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

        # Очистка таблицы Supplier перед генерацией данных
        Supplier.objects.all().delete()

        # Генерация поставщиков с проверкой ID
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

        # Генерация случайных дат за последние 5 лет
        now = timezone.now()
        five_years_ago = now - timedelta(days=5*365)

        # Генерация сущностей Delivery с случайными датами за последние 5 лет
        seed.add_entity(Delivery, 1000, {
            'supplier': lambda x: random.choice(list(suppliers)) if suppliers.exists() else None,
            'note': lambda x: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(100, 255)],
            'delivery_receipt': lambda x: random.choice([None, f"Receipt-{random.randint(100000, 999999)}"]),
            'created_at': lambda x: now - timedelta(days=random.randint(0, (now - five_years_ago).days)),
        })

        inserted_pks = seed.execute()
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(inserted_pks)} entries in Delivery.'))

        # Генерация единиц доставки
        deliveries = Delivery.objects.all()
        delivery_units_data = []  # Определяем список перед использованием

        for delivery in deliveries:
            num_units = random.randint(1, 5)  # Или используйте delivery.deliveryunits.count(), если хотите на основе существующих данных
            for _ in range(num_units):
                delivery_units_data.append({
                    'delivery_id': delivery.id,
                    'material_id': random.choice(materials).id,
                    'weight': round(random.uniform(100, 1000), 2),
                    'status': random.choice([1, 2, 3]),
                    'delivery_type': random.choice([1, 2, 3, 4]),
                    'note': "Lorem ipsum dolor sit amet, consectetur adipiscing elit."[:random.randint(100, 255)],
                })

        # Добавление единиц доставки в базу данных
        if delivery_units_data:
            DeliveryUnit.objects.bulk_create([DeliveryUnit(**data) for data in delivery_units_data])
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(delivery_units_data)} entries in DeliveryUnits.'))
        else:
            self.stdout.write(self.style.WARNING("No delivery units to create."))
