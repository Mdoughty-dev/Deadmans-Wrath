def make_maddo():
    return {
        "name": "Maddo",
        "hp": 100,
        "max_hp": 100,
        "mp": 30,
        "max_mp": 30,
        "in_party": True,
        "atb": 0,
        "spells": [
            {"name": "Hex", "cost": 10, "damage": 50},
            {"name": "Cure", "cost": 5, "heal": 40}
        ],
        "conjures": [
            {"name": "Demon Lord", "cost": 15, "damage": 80}
        ]
    }

def make_shade():
    return {
        "name": "Shade",
        "hp": 90,
        "max_hp": 90,
        "mp": 40,
        "max_mp": 40,
        "in_party": False,
        "atb": 0,
        "spells": [
            {"name": "Shadow Bolt", "cost": 8, "damage": 35},
            {"name": "Dark Heal", "cost": 6, "heal": 25}
        ],
        "conjures": []
    }

characters = [
    make_maddo(),
    make_shade()
]
