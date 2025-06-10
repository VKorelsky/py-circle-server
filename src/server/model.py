import uuid
from server.logger import get_logger
from random import choice

_logger = get_logger(__name__)

SnakeId = str
PitId = uuid.UUID


class Snake:
    def __init__(self):
        self.id: SnakeId = self._generate_random_name()

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
        return f"PitMember(id={self.id})"


class Pit:
    def __init__(self, id=uuid.uuid4()):
        self.id: PitId = id
        self.members: dict[SnakeId, Snake] = dict()

    def add_member(self, new_member: Snake):
        self.members[new_member.id] = new_member

    def remove_member(self, member_id: SnakeId):
        try:
            del self.members[member_id]
        except KeyError as e:
            return None

    def get_member(self, member_id: SnakeId) -> Snake | None:
        return self.members.get(member_id)

    def __str__(self):
        return (
            f"Pit(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )

    def __iter__(self):
        return iter(self.members.values())

    def __len__(self):
        return len(self.members)

    def __contains__(self, member_id: SnakeId):
        return member_id in self.members


class World:
    def __init__(self):
        self.pits: dict[PitId, Pit] = dict()
        self.memberships: dict[SnakeId, Pit] = dict()

    def add_pit(self, pit: Pit) -> None:
        self.pits[pit.id] = pit

    def add_member_to_pit(self, pit_id: PitId, member: Snake) -> None:
        pit = self.get_pit(pit_id)

        _logger.debug(f"Adding member to pit: {pit}")

        if pit is None:
            raise ValueError(f"Pit with id {pit_id} not found")

        pit.add_member(member)
        self.memberships[member.id] = pit

    def remove_member_from_pit(self, member_id: SnakeId) -> None:
        if not member_id in self.memberships:
            return None

        pit = self.memberships[member_id]
        pit.remove_member(member_id)

        del self.memberships[member_id]

    def get_pit(self, requested_pit_id: PitId) -> Pit | None:
        return self.pits.get(requested_pit_id)

    def get_pit_by_pit_member(self, member_id: SnakeId) -> Pit | None:
        return self.memberships.get(member_id)

    def __str__(self):
        return (
            f"World(pits="
            + str([str(pit) for pit in self.pits.values()])
            + ", memberships="
            + str(
                [
                    f"{member_id}: {str(pit.id)}"
                    for member_id, pit in self.memberships.items()
                ]
            )
            + ")"
        )

    def __iter__(self):
        return iter(self.pits.values())

    def __len__(self):
        return len(self.pits)

    def __contains__(self, pit_id: PitId):
        return pit_id in self.pits
