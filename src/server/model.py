import uuid

PitMemberId = str
PitId = uuid.UUID


class PitMember:
    def __init__(self, id):
        self.id: PitMemberId = id

    def __str__(self):
        return f"PitMember(id={self.id})"


class Pit:
    def __init__(self, id=uuid.uuid4()):
        self.id: PitId = id
        self.members: dict[PitMemberId, PitMember] = dict()

    def add_member(self, new_member: PitMember):
        self.members[new_member.id] = new_member

    def remove_member(self, member_id: PitMemberId):
        try:
            del self.members[member_id]
        except KeyError as e:
            return None

    def get_member(self, member_id: PitMemberId) -> PitMember | None:
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

    def __contains__(self, member: PitMember):
        return member.id in self.members


class World:
    def __init__(self):
        self.pits: dict[PitId, Pit] = dict()

    def add_pit(self, pit: Pit) -> None:
        self.pits[pit.id] = pit

    def get_pit(self, requested_pit_id: PitId) -> Pit | None:
        return self.pits.get(requested_pit_id)

    def get_pit_member(self, pit_id: PitId, member_id: PitMemberId) -> PitMember | None:
        pit = self.get_pit(pit_id)
        if not pit:
            return None

        return pit.get_member(member_id)

    def __iter__(self):
        return iter(self.pits.values())

    def __len__(self):
        return len(self.pits)

    def __contains__(self, pit: Pit):
        return pit.id in self.pits
