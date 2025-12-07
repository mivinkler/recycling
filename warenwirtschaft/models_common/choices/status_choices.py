class StatusChoices:
    # VORSORTIERUNG_AUSSTEHEND = 1
    VORSORTIERUNG_LAUFEND = 2
    VORSORTIERUNG_ABHOLBEREIT = 3

    AUFBEREITUNG_AUSSTEHEND = 4
    AUFBEREITUNG_LAUFEND = 5
    AUFBEREITUNG_ABHOLBEREIT = 6

    HALLE_ZWEI_AUSSTEHEND = 7
    HALLE_ZWEI_LAUFEND = 8
    HALLE_ZWEI_ABHOLBEREIT = 9

    CHOICES = [
        (VORSORTIERUNG_LAUFEND, "Vorsortierung: Laufend"),
        (VORSORTIERUNG_ABHOLBEREIT, "Vorsortierung: Abholbereit"),

        (AUFBEREITUNG_AUSSTEHEND, "Aufbereitung: Abholbereit"),
        (AUFBEREITUNG_LAUFEND, "Aufbereitung: Laufend"),
        (AUFBEREITUNG_ABHOLBEREIT, "Aufbereitung: Abholbereit"),

        (HALLE_ZWEI_AUSSTEHEND, "Halle 2: Abholbereit"),
        (HALLE_ZWEI_LAUFEND, "Halle 2: Laufend"),
        (HALLE_ZWEI_ABHOLBEREIT, "Halle 2: Abholbereit"),
    ]
