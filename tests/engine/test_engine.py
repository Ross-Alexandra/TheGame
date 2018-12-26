from threading import Thread
from unittest.mock import Mock, patch

import pygame
import pytest

from tests.test_utils import DummyEvent
from thegame.engine.engine import Engine


@patch("thegame.engine.engine.pygame.init")
@patch("thegame.engine.engine.pygame.display")
def test_init_initializes_game_window(display_mock, init_mock):

    Engine()

    assert display_mock.set_caption.called
    assert display_mock.set_mode.called
    assert init_mock.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.logging")
@patch("thegame.engine.engine.Engine._main_loop")
def test_exception_in_main_loop_is_caught(main_loop_mock, logging_mock):

    with pytest.raises(ValueError):
        main_loop_mock.side_effect = ValueError

        game = Engine()
        game.start()

    assert logging_mock.exception.called
    assert not game.running


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", list)
@patch("thegame.engine.engine.pygame.event.get")
def test_no_events_gotten_doesnt_cause_an_error(event_get_mock):
    """ This test simply ensures that no exceptions are thrown
        there is no call associated with an empty event queue."""

    event_get_mock.return_value = []

    def kill_game(_game, _event_get_mock):
        while not _event_get_mock.called:
            pass
        _game.running = False

    game = Engine()
    Thread(target=kill_game, args=(game, event_get_mock)).start()

    game.start()

    # Nothing to assert on.


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", list)
@patch("thegame.engine.engine.pygame.event.get")
def test_quit_event_causes_stopping_to_be_set_to_false(event_get_mock):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    game = Engine()
    game.start()

    assert not game.running


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.event_name", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", list)
@patch("thegame.engine.engine.logging")
@patch("thegame.engine.engine.pygame.event.get")
def test_multiple_events_both_get_handled(event_get_mock, logging_mock):
    event_get_mock.return_value = [DummyEvent("cats"), DummyEvent(pygame.QUIT)]

    game = Engine()
    game.start()

    assert not game.running
    assert logging_mock.debug.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get")
@patch("thegame.engine.engine.pygame.key.get_pressed")
@patch("thegame.engine.engine.Engine._handle_keystrokes")
def test_holding_down_character_only_counts_as_one_call(
    keystroke_handle_mock, key_pressed_mock, event_get_mock
):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]
    a_key_pressed = [0 for _ in range(355)]
    a_key_pressed[ord("a")] = True
    key_pressed_mock.return_value = a_key_pressed

    game = Engine()
    game.start()

    keystroke_handle_mock.assert_called_once_with(["a"])
