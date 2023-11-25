from cities import City
from lodging import Lodging

Case1 = [
    [
        City(name="Tokyo", country="Japan", stays_limit=5),
        City(name="Kamakura", country="Japan", stays_limit=2),
        City(name="Kyoto", country="Japan", stays_limit=4),
        City(name="Fujikawaguchiko", country="Japan", stays_limit=3),
        City(name="Kumamoto", country="Japan", stays_limit=2),
        City(name="Suwa", country="Japan", stays_limit=2),
        City(name="Niigata", country="Japan", stays_limit=2),
    ],
    [
        Lodging("Tokyo", 150),
        Lodging("Kamakura", 100),
        Lodging("Kyoto", 200),
        Lodging("Fujikawaguchiko", 240),
        Lodging("Kumamoto", 140),
        Lodging("Suwa", 120),
        Lodging("Niigata", 110),
    ],
    4000,
    13,
]

Case2 = [
    [
        City(name="Banff", country="Canada", stays_limit=4),
        City(name="Jasper", country="Canada", stays_limit=2),
        City(name="Calgary", country="Canada", stays_limit=4),
        City(name="Edmonton", country="Canada", stays_limit=3),
        City(name="Hinton", country="Canada", stays_limit=2),
    ],
    [
        Lodging("Banff", 350),
        Lodging("Jasper", 400),
        Lodging("Calgary", 200),
        Lodging("Edmonton", 170),
        Lodging("Hinton", 120),
    ],
    7000,
    8,
]

Case3 = [
    [
        City(name="Paris", country="France", stays_limit=4),
        City(name="Lyon", country="France", stays_limit=2),
        City(name="Milan", country="Italy", stays_limit=2),
        City(name="Florence", country="Italy", stays_limit=2),
        City(name="Rome", country="Italy", stays_limit=4),
        City(name="Venice", country="Italy", stays_limit=2),
        City(name="Munich", country="Germany", stays_limit=2),
        City(name="Luxembourg", country="Luxembourg", stays_limit=1),
        City(name="Gent", country="Belgium", stays_limit=2),
    ],
    [
        Lodging("Paris", 150),
        Lodging("Lyon", 120),
        Lodging("Milan", 160),
        Lodging("Florence", 150),
        Lodging("Rome", 140),
        Lodging("Venice", 180),
        Lodging("Munich", 130),
        Lodging("Luxembourg", 200),
        Lodging("Gent", 120),
    ],
    15000,
    15,
]
