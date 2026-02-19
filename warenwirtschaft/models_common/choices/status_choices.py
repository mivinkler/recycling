class StatusChoices:
    WARTET_AUF_VORSORTIERUNG = 1
    AKTIV_IN_VORSORTIERUNG = 2
    
    WARTET_AUF_ZERLEGUNG = 3
    AKTIV_IN_ZERLEGUNG = 4
    
    WARTET_AUF_HALLE_ZWEI = 5
    AKTIV_IN_HALLE_ZWEI = 6

    WARTET_AUF_ABHOLUNG = 7

    ERLEDIGT = 8


    CHOICES = [
        (WARTET_AUF_VORSORTIERUNG, "Wartet auf Vorsortierung"),
        (WARTET_AUF_ZERLEGUNG, "Wartet auf Zerlegung"),
        (WARTET_AUF_HALLE_ZWEI, "Wartet auf Halle 2"),
        (WARTET_AUF_ABHOLUNG, "Abholbereit"),

        (AKTIV_IN_VORSORTIERUNG, "In Vorsortierung"),
        (AKTIV_IN_ZERLEGUNG, "In Zerlegung"),
        (AKTIV_IN_HALLE_ZWEI, "In Halle 2"),

        (ERLEDIGT, "Erledigt"),
    ]
