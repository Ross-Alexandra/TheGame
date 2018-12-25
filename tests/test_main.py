from unittest.mock import Mock, patch

import pygame

from tests.test_utils import DummyEvent
from thegame.__main__ import start_game


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get")
def test_init_starts_the_engine(event_get_mock):
    """ This test tests that starting the game and returning sending
        a quit event will cause the game to stop."""
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    start_game()
