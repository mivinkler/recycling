# core/management/commands/db_writecheck.py
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = "Schreibt einen Testeintrag, um Schreibrechte und -pfad der DB zu prüfen."

    def handle(self, *args, **opts):
        try:
            with connection.cursor() as c:
                # -- Tabelle anlegen, falls sie fehlt
                c.execute("CREATE TABLE IF NOT EXISTS _writecheck (ts TEXT)")
                # -- Korrekte Platzhalter (%s statt ?)
                c.execute("INSERT INTO _writecheck (ts) VALUES (%s)", [timezone.now().isoformat()])
            self.stdout.write(self.style.SUCCESS("DB-Schreibtest erfolgreich."))
        except Exception as e:
            raise CommandError(f"DB-Schreibtest FEHLGESCHLAGEN: {e}")