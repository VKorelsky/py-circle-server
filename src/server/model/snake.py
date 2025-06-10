from random import choice

SnakeId = str

class Snake:
    def __init__(self, id):
        self.id: SnakeId = id
        self.display_name: SnakeId = self._generate_random_name()

    def _generate_random_name(self) -> SnakeId:
        visual_traits = [
            "striped",
            "spotted",
            "glossy",
            "coiled",
            "slim",
            "fat",
            "amber",
            "silver",
            "dusky",
            "crimson",
            "iridescent",
            "shadow",
            "long",
            "short",
            "broad",
            "mottled",
            "banded",
            "ghost",
        ]

        region_identifiers = [
            "sahara",
            "andes",
            "balkan",
            "nile",
            "amazon",
            "indus",
            "texas",
            "mongol",
            "iberian",
            "tundra",
            "burmese",
            "caspian",
            "aussie",
            "nordic",
            "sinai",
            "sumatran",
            "haitian",
            "celtic",
        ]

        species_types = [
            "cobra",
            "adder",
            "viper",
            "python",
            "krait",
            "mamba",
            "boa",
            "taipan",
            "kingsnake",
            "hognose",
            "rattler",
            "anaconda",
            "coral",
            "milksnake",
            "bushmaster",
            "boomslang",
            "whip",
            "treeviper",
        ]

        return f"{choice(visual_traits)}-{choice(region_identifiers)}-{choice(species_types)}"

    def __str__(self):
        return f"SnakePitMember(id={self.id}, display_name={self.display_name})"
