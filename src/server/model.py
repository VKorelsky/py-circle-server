import uuid


class PitMember:
    id: str

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f"PitMember(id={self.id})"


class Pit:
    id: uuid.UUID
    members: dict[str, PitMember]

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.members = dict()

    def add_member(self, new_member: PitMember):
        self.members[new_member.id] = new_member

    def remove_member(self, member_id: str):
        del self.members[member_id]

    def get_member(self, member_id: str) -> PitMember | None:
        return self.members.get(member_id)

    def __str__(self):
        return (
            f"Pit(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )


class World:
    def __init__(self):
        self.pits: dict[uuid.UUID, Pit] = dict()

    def get_pit(self, requested_pit_id: uuid.UUID) -> Pit | None:
        return self.pits.get(requested_pit_id)

    def get_pit_member(self, pit_id: uuid.UUID, member_id: str) -> PitMember | None:
        pit = self.get_pit(pit_id)
        if not pit:
            return None
        return pit.get_member(member_id)


world = World()
