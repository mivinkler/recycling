class BoxTypeChoices:
    CONTAINER = 1
    GITTERBOX = 2
    PALETTE = 3
    WAGEN = 4
    OHNE_BEHAELTER = 5

    CHOICES = [
        (CONTAINER, "Container"),
        (GITTERBOX, "Gitterbox"),
        (PALETTE, "Palette"),
        (WAGEN, "Wagen"),
        (OHNE_BEHAELTER, "Ohne Behälter"),
    ]
