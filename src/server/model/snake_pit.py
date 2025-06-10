import uuid

from server.model.snake import Snake, SnakeId

SnakePitId = uuid.UUID


class SnakePit:
    def __init__(self, id=uuid.uuid4()):
        self.id: SnakePitId = id
        self.members: dict[SnakeId, Snake] = dict()

    def add_member(self, new_member: Snake):
        self.members[new_member.display_name] = new_member

    def remove_member(self, member_id: SnakeId):
        try:
            del self.members[member_id]
        except KeyError as e:
            return None

    def get_member(self, member_id: SnakeId) -> Snake | None:
        return self.members.get(member_id)

    def __str__(self):
        return (
            f"SnakePit(id={str(self.id)}, members="
            + str([str(member) for member in self.members])
            + ")"
        )

    def __iter__(self):
        return iter(self.members.values())

    def __len__(self):
        return len(self.members)

    def __contains__(self, member_id: SnakeId):
        return member_id in self.members
