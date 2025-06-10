import uuid
import pytest
from server.model import SnakePit, Snake


class TestSnakeSnakePit:
    @pytest.fixture()
    def pit(self):
        return SnakePit()

    def test_init_default_id(self, pit):
        assert isinstance(pit.id, uuid.UUID)
        assert pit.snakes == {}

    def test_init_custom_id(self):
        custom_id = uuid.uuid4()
        pit = SnakePit(custom_id)
        assert pit.id == custom_id
        assert pit.snakes == {}

    def test_add_get_snakes(self, pit):
        snake1 = self._snake("id1")
        snake2 = self._snake("id2")

        pit.add_snake(snake1)
        pit.add_snake(snake2)

        assert len(pit.snakes) == 2
        assert pit.get_snake(snake1.id) is snake1
        assert pit.get_snake(snake2.id) is snake2

    def test_remove_snake(self, pit):
        snake1 = self._snake("id1")
        snake2 = self._snake("id2")

        pit.add_snake(snake1)
        pit.add_snake(snake2)

        pit.remove_snake(snake1)

        assert len(pit.snakes) == 1
        assert pit.get_snake(snake1.id) is None
        assert pit.get_snake(snake2.id) is snake2

    def test_remove_nonexistent_snake_does_not_raise_key_error(self, pit):
        nonexistent_snake = Snake("nonexistent")
        pit.remove_snake(nonexistent_snake)  # Should not raise KeyError

    def test_get_snake_not_exists(self, pit):
        nonexistent_snake = Snake("nonexistent")
        result = pit.get_snake(nonexistent_snake)
        assert result is None

    def _snake(self, id="snake_id"):
        return Snake(id)
