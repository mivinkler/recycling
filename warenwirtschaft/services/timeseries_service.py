from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

from django.db.models import Sum, Q
from django.db.models.functions import TruncDay

from warenwirtschaft.models.delivery_unit import DeliveryUnit

TZ = ZoneInfo("Europe/Berlin")

@dataclass(frozen=True)
class TimeSeriesParams:
    date_from: date
    date_to: date
    customer_id: int | None = None
    material_id: int | None = None
    granularity: str = "auto"  # day|week|month|quarter|year|auto

# ---------- Hilfsfunktionen (einfach gehalten) ----------

def start_of_week(d: date) -> date:
    # 🇩🇪 ISO-Wochenstart (Montag)
    return d - timedelta(days=d.weekday())

def start_of_month(d: date) -> date:
    return date(d.year, d.month, 1)

def start_of_quarter(d: date) -> date:
    q_month = ((d.month - 1) // 3) * 3 + 1
    return date(d.year, q_month, 1)

def start_of_year(d: date) -> date:
    return date(d.year, 1, 1)

def add_months(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)

def choose_granularity(p: TimeSeriesParams) -> str:
    if p.granularity != "auto":
        return p.granularity
    span_days = (p.date_to - p.date_from).days + 1
    if span_days <= 31:
        return "day"
    if span_days <= 180:
        return "week"
    if span_days <= 730:
        return "month"
    if span_days <= 1825:
        return "quarter"
    return "year"

def to_local_date(val) -> date:
    """
    🇩🇪 SQLite liefert häufig naive Datetimes aus TruncDay.
    Wir konvertieren sicher zu date.
    """
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        # naive → als lokale Zeit interpretieren
        if val.tzinfo is None:
            return val.date()
        return val.astimezone(TZ).date()
    # Fallback: versuchen zu parsen
    try:
        return datetime.fromisoformat(str(val)).date()
    except Exception:
        return None

def bucket_start_for(d: date, gran: str) -> date:
    if gran == "day":
        return d
    if gran == "week":
        return start_of_week(d)
    if gran == "month":
        return start_of_month(d)
    if gran == "quarter":
        return start_of_quarter(d)
    return start_of_year(d)  # year

def next_bucket(d: date, gran: str) -> date:
    if gran == "day":
        return d + timedelta(days=1)
    if gran == "week":
        return d + timedelta(days=7)
    if gran == "month":
        return add_months(d, 1)
    if gran == "quarter":
        return add_months(d, 3)
    return date(d.year + 1, 1, 1)

# ---------- Kernaggregation (ein Query, Rest in Python) ----------

def timeseries_weight(p: TimeSeriesParams) -> dict:
    """
    🇩🇪 Holt tägliche Summen aus der DB und faltet diese in Python
    auf week/month/quarter/year. Maximal einfach & SQLite-sicher.
    """
    gran = choose_granularity(p)

    # 🇩🇪 Basisfilter (weiche Löschung ausschließen)
    base = (
        Q(created_at__date__gte=p.date_from, created_at__date__lte=p.date_to) &
        Q(deleted_at__isnull=True) &
        Q(delivery__deleted_at__isnull=True)
    )
    if p.customer_id:
        base &= Q(delivery__customer_id=p.customer_id)
    if p.material_id:
        base &= Q(material_id=p.material_id)

    # 🇩🇪 Einmalig nach Tag aggregieren
    day_rows = (
        DeliveryUnit.objects
        .filter(base)
        .annotate(day=TruncDay("created_at"))   # SQLite-sicher
        .values("day")
        .annotate(weight_kg=Sum("weight"))
    )

    # 🇩🇪 Tageswerte → Zielbucket (gran) aufsummieren
    bucket_map = defaultdict(float)
    for r in day_rows:
        d = to_local_date(r["day"])
        if not d:
            continue
        b = bucket_start_for(d, gran)
        bucket_map[b] += float(r["weight_kg"] or 0.0)

    # 🇩🇪 Vollständige Bucket-Liste (ohne Lücken)
    #    Start-/Enddatum auf Bucket-Grenzen einschnappen
    start = bucket_start_for(p.date_from, gran)
    end = bucket_start_for(p.date_to, gran)
    buckets = []
    cur = start
    while cur <= end:
        buckets.append(cur)
        cur = next_bucket(cur, gran)

    values = [round(bucket_map.get(b, 0.0), 2) for b in buckets]
    total = round(sum(values), 2)

    return {
        "meta": {
            "from": p.date_from.isoformat(),
            "to": p.date_to.isoformat(),
            "granularity": gran,
            "timezone": "Europe/Berlin",
        },
        "buckets": [b.isoformat() for b in buckets],
        "series": {"weight_kg": values},
        "totals": {"weight_kg": total},
    }
