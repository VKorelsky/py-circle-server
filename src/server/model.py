import uuid

class CircleMember:
    id: str

    def __init__(self, socket_id):
        self.id = socket_id

    def __str__(self):
        return f"CircleMember(id={self.id})"


class Circle:
    id: uuid.UUID
    members: list[CircleMember]

    def __init__(self, id=uuid.uuid4()):
        self.id = id
        self.members = []

    def add_member(self, new_member: CircleMember):
        self.members.append(new_member)

    def remove_member(self, member_id: str):
        self.members = [m for m in self.members if str(m.id) != member_id]

    def __str__(self):
        return (
            f"Circle(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )
    
world = Circle(uuid.UUID("697d8c94-cee3-4a99-a3b6-b7cced7927fc"))

# this should really be hashmaps
def get_circle(requested_circle_id: uuid.UUID) -> Circle | None:
    for circle in world:
        if circle.id == requested_circle_id:
            return circle

    return None


def get_circle_member(circle_id: uuid.UUID, member_id: str) -> CircleMember | None:
    circle = get_circle(circle_id)

    if not circle:
        return None

    for member in circle.members:
        if str(member.id) == member_id:
            return member

    return None
