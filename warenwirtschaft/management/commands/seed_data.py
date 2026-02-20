import random
import re
from datetime import timedelta
from typing import List
from uuid import uuid4
from django.db import connection

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from warenwirtschaft.models import (
    Material, Customer, Delivery, DeliveryUnit, Unload,
    Recycling, Shipping
)

# ==============================
# Hilfsfunktionen
# ==============================

def _email_from_name(name: str) -> str:
    local = re.sub(r'[^a-z]', '', name.lower())
    return f"{local}@example.com"

def _note() -> str:
    txt = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur."
    return txt[:random.randint(0, len(txt))]

def _status_codes(model_cls, field_name: str = "status") -> List[int]:
    """
    Liefert die in der Modell-Choice-Liste vorhandenen Status-Codes.
    """
    field = model_cls._meta.get_field(field_name)
    return [choice[0] for choice in getattr(field, "choices", []) or []]

def _has_status(model_cls, code: int, field_name: str = "status") -> bool:
    """
    Prüft, ob ein Status-Code in den Choices des Modells existiert.
    """
    return code in _status_codes(model_cls, field_name)

def _barcode(prefix: str) -> str:
    """
    Erzeugt eine eindeutige Barcode-Nummer mit Prefix.
    Beispiel: L8F2A9C1
    """
    return f"{prefix}{uuid4().hex[:16].upper()}"

def _random_past_datetime(years: int = 15):
    """
    Liefert ein zufälliges Datum/Zeitpunkt innerhalb der letzten `years` Jahre.
    Sekundenauflösung, ohne Millisekunden/Mikrosekunden.
    Wird genutzt, um auto_now_add=jetzt nachträglich zu überschreiben.
    """
    days = random.randint(0, 365 * years)
    seconds = random.randint(0, 24 * 60 * 60 - 1)
    dt = timezone.now() - timedelta(days=days, seconds=seconds)
    return dt.replace(microsecond=0)  # ← keine Millisekunden

def reset_sqlite_sequence(*table_names):
    """
    Setzt AUTOINCREMENT-Zähler für SQLite zurück.
    """
    with connection.cursor() as cursor:
        for table in table_names:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name = %s;",
                [table]
            )

class Command(BaseCommand):
    help = "Befüllt die Warenwirtschaft mit Testdaten inkl. Status-Verteilung und Shipping."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        random.seed(42)

        # ==============================
        # 1) Tabellen leeren (in sicherer Reihenfolge)
        # ==============================
        DeliveryUnit.objects.all().delete()
        Unload.objects.all().delete()
        Recycling.objects.all().delete()
        Shipping.objects.all().delete()
        Delivery.objects.all().delete()
        Customer.objects.all().delete()
        Material.objects.all().delete()

        reset_sqlite_sequence(
            "warenwirtschaft_deliveryunit",
            "warenwirtschaft_unload",
            "warenwirtschaft_recycling",
            "warenwirtschaft_shipping",
            "warenwirtschaft_delivery",
            "warenwirtschaft_customer",
            "warenwirtschaft_material",
        )

        self.stdout.write(self.style.WARNING("Alle relevanten Tabellen wurden geleert."))

        # ==============================
        # 2) Stammdaten erzeugen: Material & Kunde
        # ==============================
        materials_data = [
            "Laptop", "PC", "Dockingstation", "Monitor", "Bildröhren",
            "Kabel", "Gemischte Teile", "Netzteile", "Festplatten",
            "Leiterplatten", "Drucker", "Flat-TV/TFT-Monitore", "CRT",
            "Restmüll", "E-Schrott", "DVD/CD", "Batterien", "Schadstoffe"
        ]
        Material.objects.bulk_create([Material(name=name) for name in materials_data], ignore_conflicts=True)

        streets = ["Hauptstraße", "Bahnhofstraße", "Friedrichstraße", "Schillerstraße", "Goethestraße"]
        cities  = ["München", "Germering", "Freising", "Erding", "Starnberg"]
        companies = [
            "Müller GmbH", "Schmidt GmbH", "Fischer Bau", "Weber Elektro", "Meier GmbH", "Hoffmann IT",
            "Becker Maschinen", "Zimmermann GmbH", "Schneider GmbH", "Bauer Fenster", "Klein und Müller GmbH",
            "Kaiser Bau", "Richter GmbH", "Bergmann Handel", "Wagner und Partner", "Böhm Consulting", "Neumann und Sohn",
            "Graf Technik", "Lang GmbH", "Sauer Möbel", "Peters GmbH", "Jäger GmbH", "Lang Bauunternehmen",
            "Schröder Engineering", "Hansen Möbelbau", "Lenz GmbH", "Bender GmbH", "Böttcher GmbH", "Weber GmbH",
            "Löffler Metallbau", "Kuhn und Schmidt", "Meyer Maschinenbau", "Fuchs und Partner", "Lenz IT",
            "Haas und Söhne", "Wolff und Müller", "Schmitt und Co.", "Stern Elektro GmbH", "Eckert GmbH"
        ]

        customers = [
            Customer(
                name=name,
                street=f"{random.choice(streets)} {random.randint(1, 300)}",
                postal_code=str(random.randint(80000, 89999)),
                city=random.choice(cities),
                phone=f"+49{random.randint(100000000, 999999999)}",
                email=_email_from_name(name),
                note=_note(),
            )
            for name in companies
        ]
        Customer.objects.bulk_create(customers, ignore_conflicts=True)
        customers = list(Customer.objects.all())
        materials = list(Material.objects.all())

        self.stdout.write(self.style.SUCCESS(f"Materialien: {Material.objects.count()} • Kunden: {Customer.objects.count()}"))

        # ==============================
        # 3) Deliveries erzeugen (10.000 über 15 Jahre)
        #     auto_now_add überschreiben wir danach per bulk_update.
        # ==============================
        deliveries: List[Delivery] = [
            Delivery(
                customer=random.choice(customers),
                delivery_receipt=str(random.randint(100000, 999999)),
                note=_note(),
                # kein created_at hier → auto_now_add setzt „jetzt“
            )
            for _ in range(10_000)
        ]
        Delivery.objects.bulk_create(deliveries, batch_size=2000)

        deliveries = list(Delivery.objects.all().only("id", "created_at"))
        for d in deliveries:
            d.created_at = _random_past_datetime(15)
        Delivery.objects.bulk_update(deliveries, ["created_at"], batch_size=2000)

        self.stdout.write(self.style.SUCCESS(f"Deliveries: {len(deliveries)}"))

        # ==============================
        # 4) DeliveryUnits
        #     a) Standard: Status = 8 (Erledigt)
        #     b) Zusätzlich: je 10 mit Status 1/2/3, wenn vorhanden
        # ==============================
        dus: List[DeliveryUnit] = []

        # a) Standard-Einheiten (Erledigt) – für jede Lieferung 1–4 Einheiten
        deliveries_full = list(Delivery.objects.all().only("id"))
        for d in deliveries_full:
            for _ in range(random.randint(1, 4)):
                dus.append(DeliveryUnit(
                    delivery=d,
                    box_type=random.choice([1, 2, 3, 4]),
                    material=random.choice(materials),
                    weight=round(random.uniform(80, 800), 2),
                    status=8, 
                    note=_note(),
                    barcode=_barcode("L"),
                ))
        DeliveryUnit.objects.bulk_create(dus, batch_size=2000)

        # b) Zusatz je Status (1/2/3) – je 10 Einträge, falls vorhanden
        extra_du: List[DeliveryUnit] = []
        for status_code in (1, 2):
            if _has_status(DeliveryUnit, status_code):
                for _ in range(10):
                    extra_du.append(DeliveryUnit(
                        delivery=random.choice(deliveries_full),
                        box_type=random.choice([1, 2, 3, 4]),
                        material=random.choice(materials),
                        weight=round(random.uniform(80, 800), 2),
                        status=status_code,
                        note=_note(),
                        barcode=_barcode("L"),
                    ))
        if extra_du:
            DeliveryUnit.objects.bulk_create(extra_du, batch_size=2000)

        # Historische Zeitstempel für alle DeliveryUnits (letzte 15 Jahre)
        du_all = list(DeliveryUnit.objects.all().only("id", "created_at"))
        for du in du_all:
            du.created_at = _random_past_datetime(15)
        DeliveryUnit.objects.bulk_update(du_all, ["created_at"], batch_size=2000)

        self.stdout.write(self.style.SUCCESS(f"DeliveryUnits total: {DeliveryUnit.objects.count()}"))

        # ==============================
        # 5) Unloads (m2m zu DeliveryUnit)
        #     a) Standard: Status = 8 (Erledigt)
        #     b) Zusätzlich: je 10 für 1/2/3 (falls vorhanden)
        # ==============================
        unload_objs: List[Unload] = [
            Unload(
                box_type=random.choice([1, 2, 3, 4]),
                material=random.choice(materials),
                weight=round(random.uniform(10, 150), 2),
                status=8,  # Standard-Status
                note=_note(),
                barcode=_barcode("V"),
            )
            for _ in range(400)
        ]
        Unload.objects.bulk_create(unload_objs, batch_size=1000)

        # b) Zusatz je Status (1/2/3) — je 10 Einträge
        extra_unloads: List[Unload] = []
        for status_code in (3, 4, 7):
            if _has_status(Unload, status_code):
                for _ in range(10):
                    extra_unloads.append(Unload(
                        box_type=random.choice([1, 2, 3, 4]),
                        material=random.choice(materials),
                        weight=round(random.uniform(10, 150), 2),
                        status=status_code,
                        note=_note(),
                        barcode=_barcode("V"),
                    ))
        if extra_unloads:
            Unload.objects.bulk_create(extra_unloads, batch_size=1000)

        # Historische Zeitstempel für alle Unloads (letzte 15 Jahre)
        u_all = list(Unload.objects.all().only("id", "created_at"))
        for u in u_all:
            u.created_at = _random_past_datetime(15)
        Unload.objects.bulk_update(u_all, ["created_at"], batch_size=2000)

        # m2m-Beziehungen setzen (je Unload 1–3 beliebige DeliveryUnits)
        all_du = list(DeliveryUnit.objects.all().only("id"))
        unload_objs_all = list(Unload.objects.all().only("id"))  # nach Zeitstempel-Update ok
        for u in unload_objs_all:
            attach = random.sample(all_du, k=random.randint(1, min(3, len(all_du))))
            # add akzeptiert PKs – wir geben IDs für Performance
            u.delivery_units.add(*[du.id for du in attach])

        self.stdout.write(self.style.SUCCESS(f"Unloads total: {Unload.objects.count()}"))

        # ==============================
        # 6) Recycling (m2m zu Unload)
        #     a) Standard: Status = 4 (Erledigt)
        #     b) Zusätzlich: je 10 für 1/3 (falls vorhanden; 2 gibt es hier evtl. nicht)
        # ==============================
        recycling_objs: List[Recycling] = [
            Recycling(
                box_type=random.choice([5, 6]),
                material=random.choice(materials),
                weight=round(random.uniform(5, 120), 2),
                status=8,
                note=_note(),
                barcode=_barcode("Z"),
            )
            for _ in range(500)
        ]
        Recycling.objects.bulk_create(recycling_objs, batch_size=1000)

        # b) Zusatz je Status (1 und 3) — je 10 Einträge
        extra_rec: List[Recycling] = []
        for status_code in (5, 6, 7):
            if _has_status(Recycling, status_code):
                for _ in range(10):
                    extra_rec.append(Recycling(
                        box_type=random.choice([1, 2, 3, 4]),
                        material=random.choice(materials),
                        weight=round(random.uniform(5, 120), 2),
                        status=status_code,
                        note=_note(),
                        barcode=_barcode("A"),
                    ))
        if extra_rec:
            Recycling.objects.bulk_create(extra_rec, batch_size=1000)

        # Historische Zeitstempel für alle Recyclings (letzte 15 Jahre)
        r_all = list(Recycling.objects.all().only("id", "created_at"))
        for r in r_all:
            r.created_at = _random_past_datetime(15)
        Recycling.objects.bulk_update(r_all, ["created_at"], batch_size=2000)

        # m2m: Recyclings ↔ Unloads
        all_unloads = list(Unload.objects.all().only("id"))
        rec_all = list(Recycling.objects.all().only("id"))
        for r in rec_all:
            attach = random.sample(all_unloads, k=random.randint(1, min(3, len(all_unloads))))
            r.unloads.add(*[u.id for u in attach])

        self.stdout.write(self.style.SUCCESS(f"Recyclings total: {Recycling.objects.count()}"))

        # ==============================
        # 7) Shipping (finale Stufe)
        #     - Erzeugen Shipping-Objekte
        #     - Unloads/Recyclings (falls FK shipping existiert) werden auf Shipping gesetzt
        # ==============================
        bereite_unloads = list(Unload.objects.filter(status=3).only("id"))
        bereite_recycling = list(Recycling.objects.filter(status=3).only("id"))

        # Falls keine Status-3-Objekte existieren, nehmen wir ein paar erledigte als Demo.
        if not bereite_unloads:
            bereite_unloads = list(Unload.objects.order_by('?').only("id")[:20])
        if not bereite_recycling:
            bereite_recycling = list(Recycling.objects.order_by('?').only("id")[:20])

        shippings: List[Shipping] = [
            Shipping(
                customer=random.choice(customers),
                certificate=random.randint(100000, 999999),
                transport=random.choice([1, 2]),
                note=_note(),
                barcode=_barcode("V"),  # Versand-Barcode
                # created_at wird per auto_now_add gesetzt
            )
            for _ in range(20)
        ]
        Shipping.objects.bulk_create(shippings, batch_size=100)

        # Historische Zeitstempel für Shipping (ebenfalls 15 Jahre)
        s_all = list(Shipping.objects.all().only("id", "created_at"))
        for s in s_all:
            s.created_at = _random_past_datetime(15)
        Shipping.objects.bulk_update(s_all, ["created_at"], batch_size=1000)

        # Zuweisung: pro Shipping ein paar Unloads/Recyclings (über FK 'shipping', falls vorhanden)
        shippings = list(Shipping.objects.all().only("id"))
        for ship in shippings:
            picked_unloads = random.sample(
                bereite_unloads, k=min(len(bereite_unloads), random.randint(1, 5))
            ) if bereite_unloads else []
            picked_recs = random.sample(
                bereite_recycling, k=min(len(bereite_recycling), random.randint(1, 5))
            ) if bereite_recycling else []

            # FK setzen (nur wenn diese Felder in den Modellen existieren)
            if picked_unloads:
                Unload.objects.filter(id__in=[u.id for u in picked_unloads]).update(shipping=ship)

            if picked_recs:
                Recycling.objects.filter(id__in=[r.id for r in picked_recs]).update(shipping=ship)

        self.stdout.write(self.style.SUCCESS(f"Shipping total: {Shipping.objects.count()}"))
