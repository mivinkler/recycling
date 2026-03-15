"""Werkzeuge fuer Listenansichten mit Suche, Filtern und Sortierung.

Die Datei hat zwei Aufgaben:
1. Class `SearchService` kapselt die eigentliche Suchlogik.
2. Kleine Helferfunktionen erzeugen wiederverwendbare `field_configs`,
   damit Listenansichten keine langen, fast identischen Dictionaries
   mehr enthalten muessen.
"""

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.dateparse import parse_date

from warenwirtschaft.services.pagination_service import PaginationPreferenceMixin
from warenwirtschaft.services.sorting_service import SortingService

FILTER_TEXT = "text"
FILTER_DATE = "date"
FILTER_CHOICE = "choice"
DEFAULT_TEXT_LOOKUP = "icontains"
LEGACY_FILTER_PARAMS = ("search", "date_start", "date_end", "status_filter")


def text_filter(field, label, *, lookup=DEFAULT_TEXT_LOOKUP, **overrides):
    """Erzeugt einen einfachen Texteingabe-Filter."""
    return {
        "field": field,
        "label": label,
        "type": FILTER_TEXT,
        "lookup": lookup,
        **overrides,
    }


def exact_text_filter(field, label, **overrides):
    """Kurzform fuer Textfilter mit exakter Uebereinstimmung."""
    return text_filter(field, label, lookup="exact", **overrides)


def date_filter(field, label, **overrides):
    """Erzeugt einen Datumsbereichs-Filter mit Von/Bis-Eingabe."""
    return {
        "field": field,
        "label": label,
        "type": FILTER_DATE,
        **overrides,
    }


def choice_filter(field, label, choices, *, filter_field=None, **overrides):
    """Erzeugt einen Select-Filter auf Basis vorgegebener Auswahlwerte."""
    return {
        "field": field,
        "label": label,
        "type": FILTER_CHOICE,
        "choices": choices,
        "filter_field": filter_field or field,
        **overrides,
    }


def queryset_choice_filter(
    field,
    label,
    queryset,
    *,
    filter_field=None,
    value_field="id",
    label_field="name",
    **overrides,
):
    """Erzeugt einen Select-Filter aus einem QuerySet oder einer QuerySet-Fabrik."""

    def resolve_queryset_choices():
        resolved_queryset = queryset() if callable(queryset) else queryset
        return resolved_queryset.order_by(label_field).values_list(value_field, label_field)

    return choice_filter(
        field,
        label,
        resolve_queryset_choices,
        filter_field=filter_field,
        **overrides,
    )


def model_field_choice_filter(
    model,
    field,
    label,
    *,
    model_field_name=None,
    filter_field=None,
    **overrides,
):
    """Erzeugt einen Select-Filter aus den `choices` eines Modellfelds."""
    model_field_name = model_field_name or field.rsplit("__", 1)[-1]
    return choice_filter(
        field,
        label,
        lambda: model._meta.get_field(model_field_name).choices,
        filter_field=filter_field,
        **overrides,
    )


def id_filter(field="id", label="ID", **overrides):
    """Standardfilter fuer technische IDs."""
    return exact_text_filter(field, label, **overrides)


def created_at_filter(field="created_at", label="Datum", **overrides):
    """Standardfilter fuer ein Erstellungsdatum."""
    return date_filter(field, label, **overrides)


def inactive_at_filter(field="inactive_at", label="Erledigt am", **overrides):
    """Standardfilter fuer ein Abschluss- oder Inaktiv-Datum."""
    return date_filter(field, label, **overrides)


def status_filter(model, field="status", label="Status", **overrides):
    """Standardfilter fuer Status-Choices eines Modells."""
    return model_field_choice_filter(model, field, label, model_field_name="status", **overrides)


def box_type_filter(model, field="box_type", label="Beh\u00e4lter", **overrides):
    """Standardfilter fuer Behaeltertypen."""
    return model_field_choice_filter(model, field, label, model_field_name="box_type", **overrides)


def transport_filter(model, field="transport", label="Transport", **overrides):
    """Standardfilter fuer Transportarten."""
    return model_field_choice_filter(model, field, label, model_field_name="transport", **overrides)


def customer_filter(queryset, field="customer__name", label="Kunde", filter_field="customer_id", **overrides):
    """Standardfilter fuer Kunden oder Lieferanten mit Name als Anzeige."""
    return queryset_choice_filter(field, label, queryset, filter_field=filter_field, **overrides)


def material_filter(queryset, field="material__name", label="Material", filter_field="material_id", **overrides):
    """Standardfilter fuer Material-Auswahllisten."""
    return queryset_choice_filter(field, label, queryset, filter_field=filter_field, **overrides)


def barcode_filter(field="barcode", label="Barcode", **overrides):
    """Standardfilter fuer Barcodes mit Teilstring-Suche."""
    return text_filter(field, label, **overrides)


def note_filter(field="note", label="Anmerkung", **overrides):
    """Standardfilter fuer Freitext-Notizen."""
    return text_filter(field, label, **overrides)


def weight_filter(field="weight", label="Gewicht (kg)", **overrides):
    """Standardfilter fuer Gewichte, hier bewusst mit exakter Suche."""
    return exact_text_filter(field, label, **overrides)


class SearchService:
    """Bereitet Suchfelder fuer die UI vor und wendet sie auf QuerySets an.

    Der Service arbeitet in zwei Modi:
    1. Neuer Modus mit `field_configs`:
       Jede Listenansicht beschreibt ihre Filter explizit.
    2. Kompatibilitaetsmodus mit `search_fields`:
       Aeltere Views koennen weiter ueber ein freies Suchfeld arbeiten.
    """

    def __init__(self, request, search_fields=None, choices_fields=None, search_filters=None, field_configs=None):
        self.request = request
        self.params = request.GET
        self.field_configs = list(field_configs or [])
        self.search_fields = self._normalize_search_fields(search_fields)
        self.choices_fields = choices_fields or {}
        self.search_filters = list(search_filters or [])

        if self.field_configs:
            self.search_fields = [config["field"] for config in self.field_configs]
            if not self.search_filters:
                self.search_filters = self.build_search_filters()

    def _normalize_search_fields(self, search_fields):
        """Zieht aus Tupeln nur den eigentlichen Feldnamen heraus."""
        normalized_fields = []
        for field in search_fields or []:
            normalized_fields.append(field[0] if isinstance(field, tuple) else field)
        return normalized_fields

    def get_sort_fields(self):
        """Liefert die Felder, die im Sortiermenue angeboten werden sollen."""
        return list(self.search_fields)

    def get_active_fields(self):
        """Liefert Feldname plus Anzeige-Label fuer das Sortiermenue."""
        if self.search_filters:
            return [(search_filter["field"], search_filter["label"]) for search_filter in self.search_filters]
        return [(field, field) for field in self.search_fields]

    def get_context_data(self):
        """Stellt alle UI-Daten fuer Such- und Sortierkomponenten bereit."""
        return {
            "request": self.request,
            "active_fields": self.get_active_fields(),
            "search_filters": self.search_filters,
            "has_active_filters": self.has_active_filters(),
            "search_query": self.params.get("search", ""),
            "sort_param": self.params.get("sort", ""),
        }

    def has_active_filters(self):
        """Prueft, ob der Benutzer aktuell irgendeinen Filter gesetzt hat."""
        if self.search_filters:
            return any(self._filter_has_value(search_filter) for search_filter in self.search_filters)
        return any(self.params.get(param) for param in LEGACY_FILTER_PARAMS)

    def _filter_has_value(self, search_filter):
        """Unterscheidet zwischen Datumsfiltern und einfachen Einzelwerten."""
        if search_filter["type"] == FILTER_DATE:
            return bool(search_filter.get("from_value") or search_filter.get("to_value"))
        return bool(search_filter.get("value"))

    def build_search_filters(self):
        """Bereitet rohe `field_configs` fuer die Template-Ausgabe auf."""
        return [self._build_filter_definition(config) for config in self.field_configs]

    def _build_filter_definition(self, config):
        """Ergaenzt eine Konfiguration um Request-Werte und UI-Metadaten."""
        search_filter = config.copy()
        field = search_filter["field"]
        filter_type = search_filter.get("type", FILTER_TEXT)
        param = search_filter.get("param", field.replace("__", "_"))

        search_filter["type"] = filter_type
        search_filter["filter_field"] = search_filter.get("filter_field", field)

        if filter_type == FILTER_DATE:
            search_filter["from_param"] = f"{param}_from"
            search_filter["to_param"] = f"{param}_to"
            search_filter["from_value"] = self._get_param_value(search_filter["from_param"])
            search_filter["to_value"] = self._get_param_value(search_filter["to_param"])
            return search_filter

        search_filter["param"] = param
        search_filter["value"] = self._get_param_value(param)

        if filter_type == FILTER_CHOICE:
            search_filter["choices"] = self._serialize_choices(search_filter.get("choices", []))
            return search_filter

        search_filter["lookup"] = search_filter.get("lookup", DEFAULT_TEXT_LOOKUP)
        return search_filter

    def _get_param_value(self, param_name):
        """Liest einen GET-Parameter und entfernt ueberfluessige Leerzeichen."""
        return self.params.get(param_name, "").strip()

    def _serialize_choices(self, choices):
        """Formatiert Choice-Quellen fuer das Template in ein einheitliches Format."""
        return [
            {"value": str(value), "label": label}
            for value, label in self._resolve_choices(choices)
        ]

    def _resolve_choices(self, choices):
        """Erlaubt sowohl Listen als auch Callables als Choice-Quelle."""
        if callable(choices):
            choices = choices()
        return list(choices)

    def apply_search(self, queryset):
        """Wendet entweder konfigurierte Filter oder die alte Freitextsuche an."""
        if self.search_filters:
            return self._apply_configured_filters(queryset)

        queryset = self._apply_legacy_text_search(queryset)
        queryset = self._apply_legacy_date_filter(queryset)
        return self._apply_legacy_choice_filters(queryset)

    def _apply_configured_filters(self, queryset):
        """Laeuft der Reihe nach ueber alle definierten Suchfilter."""
        for search_filter in self.search_filters:
            if search_filter["type"] == FILTER_DATE:
                queryset = self._apply_date_range_filter(queryset, search_filter)
                continue

            if not search_filter.get("value"):
                continue

            queryset = self._apply_value_filter(queryset, search_filter)

        return queryset

    def _apply_date_range_filter(self, queryset, search_filter):
        """Wendet einen Von/Bis-Datumsbereich auf ein Feld an."""
        field = search_filter["field"]
        parsed_from = self._parse_date_value(search_filter.get("from_value"))
        parsed_to = self._parse_date_value(search_filter.get("to_value"))

        if parsed_from:
            queryset = queryset.filter(**{f"{field}__date__gte": parsed_from})
        if parsed_to:
            queryset = queryset.filter(**{f"{field}__date__lte": parsed_to})

        return queryset

    def _parse_date_value(self, value):
        """Parst Datumswerte nur dann, wenn ueberhaupt etwas eingegeben wurde."""
        if not value:
            return None
        return parse_date(value)

    def _apply_value_filter(self, queryset, search_filter):
        """Wendet Text- oder Choice-Filter robust auf das QuerySet an."""
        filter_type = search_filter["type"]
        filter_field = search_filter.get("filter_field", search_filter["field"])
        value = search_filter["value"]

        try:
            if filter_type == FILTER_CHOICE:
                return queryset.filter(**{filter_field: value})

            lookup = search_filter.get("lookup", DEFAULT_TEXT_LOOKUP)
            return queryset.filter(**{f"{filter_field}__{lookup}": value})
        except (TypeError, ValueError, ValidationError):
            return queryset

    def _apply_legacy_text_search(self, queryset):
        """Alte Freitextsuche fuer Views ohne `field_configs`."""
        search_query = self._get_param_value("search").lower()
        if not search_query:
            return queryset

        q_objects = Q()

        for field, choices in self.choices_fields.items():
            label_to_value = {label.lower(): value for value, label in choices}
            if search_query in label_to_value:
                q_objects |= Q(**{field: label_to_value[search_query]})

        for field in self.search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})

        return queryset.filter(q_objects)

    def _apply_legacy_date_filter(self, queryset):
        """Alte Datumsfilterung auf Basis von `created_at`."""
        date_start = self._parse_date_value(self._get_param_value("date_start"))
        date_end = self._parse_date_value(self._get_param_value("date_end"))

        if date_start:
            queryset = queryset.filter(created_at__date__gte=date_start)
        if date_end:
            queryset = queryset.filter(created_at__date__lte=date_end)

        return queryset

    def _apply_legacy_choice_filters(self, queryset):
        """Alte Statusauswahl fuer Views, die noch kein `field_configs` nutzen."""
        status_filter = self._get_param_value("status_filter").lower()
        choices = self.choices_fields.get("status")
        if not choices or not status_filter:
            return queryset

        label_to_value = {label.lower(): value for value, label in choices}
        if status_filter in label_to_value:
            return queryset.filter(status=label_to_value[status_filter])

        return queryset


class SearchableListViewMixin(PaginationPreferenceMixin):
    """Mischt Suche, Sortierung und optionale `distinct()`-Logik in ListViews ein."""

    field_configs = []
    search_distinct = False

    def get_field_configs(self):
        """Ermoeglicht Unterklassen, Konfiguration dynamisch zu erzeugen."""
        return self.field_configs

    def get_search_service(self):
        """Erzeugt den Service nur einmal pro Request."""
        if not hasattr(self, "_search_service"):
            self._search_service = SearchService(self.request, field_configs=self.get_field_configs())
        return self._search_service

    def apply_search_and_sort(self, queryset):
        """Fuehrt typische Schritte für ListView aus."""
        search_service = self.get_search_service()
        sorting_service = SortingService(self.request, search_service.get_sort_fields())

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        if self.search_distinct:
            queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        """Erweitert den Standard-Context um Such- und Sortierdaten."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_search_service().get_context_data())
        return context
