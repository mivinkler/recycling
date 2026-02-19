# from .deactivate_time_mixin import DeactivateTimeMixin
from .weight_history_mixin import WeightHistoryMixin

__all__ = [
    # "DeactivateTimeMixin",
    "WeightHistoryMixin",
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