def make_creeper():
    return {
        "name": "Creeper",
        "hp": 500,
        "max_hp": 500,
        "atb": 0,
        "turn": False,
        "attacks": [
        {"name": "Knife Stab", "damage": 25, "type": "physical"},
        {"name": "Knife Fury", "damage": 35, "type": "physical"},
        {"name": "Poison Cut", "damage": 15, "type": "physical", "effect": "poison", "duration": 3},
        {"name": "Fire Breath", "damage": 30, "type": "magic", "element": "fire"}
        ],
        "attack_index": 0,
        "stats": {
        "attack": 12,
        "magic": 10,
        "defence": 8,
        "speed": 10,
        "agility": 8
        },
        "affinities": {
            "dark": "resist",
            "fire": "weak",
            "ice": "normal",
        }
    }


def make_slug():
    return {
        "name": "Slug Horror",
        "hp": 140,
        "max_hp": 140,
        "atb": 0,
        "turn": False,
        "attack_cycle": ["Bite", "Slime Spit", "Body Slam"],
        "attack_index": 0,
        "stats": {
        "attack": 12,
        "magic": 10,
        "defence": 8,
        "speed": 10,
        "agility": 8
        },
        "affinities": {
            "dark": "resist",
            "fire": "weak",
            "ice": "normal",
        }
    }

