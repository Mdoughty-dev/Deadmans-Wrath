def make_maddo():
    return {
        "name": "Maddo",
        "hp": 500,
        "max_hp": 500,
        "mp": 150,
        "max_mp": 150,
        "in_party": True,
        "atb": 0,
        "stats": {
        "attack": 12,
        "magic": 10,
        "defence": 8,
        "speed": 10,
        "agility": 8
        },
        "spells": [
            {"name": "Hex", "cost": 10, "damage": 50, "effect": "hex", "projectile_speed": 24, "element": "dark"},
            {"name": "Cure", "cost": 5, "heal": 40, "element": "holy"},
        ],
        "conjures": [
            {"name": "Demon Lord", "cost": 15, "damage": 80, "element": "dark"}
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
        "conjures": [],
        "stats": {
        "attack": 12,
        "magic": 10,
        "defence": 8,
        "speed": 10,
        "agility": 8
        }, 
    }

characters = [
    make_maddo(),
    make_shade()
]

