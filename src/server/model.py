import uuid

class PitMember:
    id: str

    def __init__(self, socket_id):
        self.id = socket_id

    def __str__(self):
        return f"PitMember(id={self.id})"


class Pit:
    id: uuid.UUID
    members: list[PitMember]

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.members = []

    def add_member(self, new_member: PitMember):
        self.members.append(new_member)

    def remove_member(self, member_id: str):
        self.members = [m for m in self.members if str(m.id) != member_id]

    def __str__(self):
        return (
            f"Pit(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )
    
# World now contains multiple pits
world: list[Pit] = []

def get_pit(requested_pit_id: uuid.UUID) -> Pit | None:
    for pit in world:
        if pit.id == requested_pit_id:
            return pit
    return None


def get_pit_member(pit_id: uuid.UUID, member_id: str) -> PitMember | None:
    pit = get_pit(pit_id)

    if not pit:
        return None

    for member in pit.members:
        if str(member.id) == member_id:
            return member

    return None
