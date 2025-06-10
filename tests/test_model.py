import uuid
import pytest

from server.model import PitMember, Pit, World


class TestPitMember:
    def test_init(self):
        member = PitMember("test_id")
        assert member.id == "test_id"

    def test_str(self):
        member = PitMember("test_id")
        assert str(member) == "PitMember(id=test_id)"


class TestPit:
    @pytest.fixture()
    def pit(self):
        return Pit()

    def test_init_default_id(self, pit):
        assert isinstance(pit.id, uuid.UUID)
        assert pit.members == {}

    def test_init_custom_id(self):
        custom_id = uuid.uuid4()
        pit = Pit(custom_id)
        assert pit.id == custom_id
        assert pit.members == {}

    def test_add_get_members(self, pit):
        member1 = self._pit_member()
        member2 = self._pit_member()

        pit.add_member(member1)
        pit.add_member(member2)

        assert len(pit.members) == 2
        assert pit.get_member(member1.id) == member1
        assert pit.get_member(member2.id) == member2

    def test_remove_member(self, pit):
        member1 = self._pit_member()
        member2 = self._pit_member()

        pit.add_member(member1)
        pit.add_member(member2)

        pit.remove_member(member1.id)

        assert len(pit.members) == 1
        assert pit.get_member(member1.id) is None

        assert pit.get_member(member2.id) == member2

    def test_remove_nonexistent_member_does_not_raise_key_error(self):
        pit = Pit()
        pit.remove_member("nonexistent")  # Should not raise KeyError

    def test_get_member_not_exists(self, pit):
        result = pit.get_member("nonexistent")
        assert result is None

    def test_str(self, pit):
        member = self._pit_member()
        pit.add_member(member)

        result = str(pit)

        assert f"Pit(id={str(pit.id)}" in result
        assert member.id in result

    def _pit_member(self):
        return PitMember(str(uuid.uuid4()))


class TestWorld:
    @pytest.fixture()
    def world(self) -> World:
        return World()

    def test_init(self, world):
        assert len(world) == 0

    def test_add_get_pit(self, world):
        pit = self._pit()

        world.add_pit(pit)
        result = world.get_pit(pit.id)

        assert result is pit

    def test_add_member_to_pit(self, world):
        pit = self._pit()
        world.add_pit(pit)

        member = self._pit_member()
        world.add_member_to_pit(pit.id, member)

        assert member.id in pit
        assert pit.get_member(member.id) is member
        assert world.memberships[member.id] is pit

    def test_add_member_to_non_existent_pit(self, world):
        member = self._pit_member()
        
        with pytest.raises(ValueError):
            world.add_member_to_pit(uuid.uuid4(), member)

    def test_remove_member_from_pit(self, world):
        pit = self._pit()
        member = self._pit_member()
        world.add_pit(pit)

        world.add_member_to_pit(pit.id, member)

        assert member.id in pit
        assert pit.get_member(member.id) is member
        assert world.memberships[member.id] is pit

        world.remove_member_from_pit(member.id)

        assert member.id not in pit
        assert pit.get_member(member.id) is None
        assert member.id not in world.memberships

    def test_get_pit_not_exists(self, world):
        nonexistent_id = uuid.uuid4()
        assert world.get_pit(nonexistent_id) is None

    def test_get_pit_by_pit_member(self, world):
        first_pit = self._pit()
        second_pit = self._pit()
        first_member = self._pit_member()
        second_member = self._pit_member()

        world.add_pit(first_pit)
        world.add_pit(second_pit)

        world.add_member_to_pit(first_pit.id, first_member)
        world.add_member_to_pit(second_pit.id, second_member)

        assert world.get_pit_by_pit_member(first_member.id) is first_pit
        assert world.get_pit_by_pit_member(second_member.id) is second_pit

    def test_get_pit_by_pit_member_not_exists(self, world):
        nonexistent_pit_member_id = str(uuid.uuid4())

        assert world.get_pit_by_pit_member(nonexistent_pit_member_id) is None

    def test_contains_pit(self, world):
        pit = self._pit()
        world.add_pit(pit)

        assert pit.id in world

    def test_iter(self, world):
        pit1 = self._pit()
        pit2 = self._pit()
        world.add_pit(pit1)
        world.add_pit(pit2)

        world_as_list = list(world)

        assert len(world_as_list) == 2
        assert pit1 in world_as_list
        assert pit2 in world_as_list

    def _pit_member(self):
        return PitMember(str(uuid.uuid4()))

    def _pit(self):
        return Pit(uuid.uuid4())
