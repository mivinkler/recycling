from .box_type_choices import BoxTypeChoices
from .status_choices import StatusChoices
from .transport_choices import TransportChoices
from .purpose_choices import PurposeChoices

__all__ = [
    "BoxTypeChoices",
    "StatusChoices",
    "TransportChoices",
    "PurposeChoices",
]

# Hinweis:
# Das Attribut `__all__` legt fest, welche Klassen als öffentliche API dieses
# Moduls gelten. Das ist nicht zwingend erforderlich, sorgt aber für eine
# klarere Struktur:
#
# - Nur die hier aufgeführten Namen werden bei `from ... import *` exportiert.
# - IDEs erkennen dadurch leichter die offiziell vorgesehenen Objekte.
#
# Ohne `__all__` funktioniert der Code ebenfalls, jedoch weniger eindeutig.