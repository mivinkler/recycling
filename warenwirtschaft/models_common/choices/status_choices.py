class StatusChoices:
    WARTET_AUF_VORSORTIERUNG = 1
    WARTET_AUF_ZERLEGUNG = 2
    WARTET_AUF_HALLE_ZWEI = 3
    
    IN_VORSORTIERUNG = 4
    IN_ZERLEGUNG = 5
    IN_HALLE_ZWEI = 6

    ABHOLBEREIT = 7

    CHOICES = [
        (WARTET_AUF_VORSORTIERUNG, "Wartet auf Vorsortierung"),
        (WARTET_AUF_ZERLEGUNG, "Wartet auf Zerlegung"),
        (WARTET_AUF_HALLE_ZWEI, "Wartet auf Halle 2"),

        (IN_VORSORTIERUNG, "In Vorsortierung"),
        (IN_ZERLEGUNG, "In Zerlegung"),
        (IN_HALLE_ZWEI, "In Halle 2"),

        (ABHOLBEREIT, "Abholbereit"),
    ]
