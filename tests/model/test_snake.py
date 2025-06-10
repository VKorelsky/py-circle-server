from server.model.snake import Snake


class TestSnake:
    def test_init(self):
        snake = Snake("12")
        assert snake.id == "12"
        assert snake.display_name is not None

    def test_str(self):
        snake = Snake("12")
        assert (
            str(snake)
            == f"SnakePitMember(id={snake.id}, display_name={snake.display_name})"
        )
