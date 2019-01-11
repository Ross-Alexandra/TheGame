from threading import Thread
from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from tests.test_utils import DummyEvent
from thegame.engine import BaseGame, BaseMenu, Engine


def generate_keystroke_list(characters_pressed):
    key_presses = [0 for _ in range(355)]

    for key in characters_pressed:
        key_presses[ord(key)] = True

    return key_presses


@patch("thegame.engine.engine.pygame.init")
@patch("thegame.engine.engine.pygame.display")
def test_init_initializes_game_window(display_mock, init_mock):

    Engine(Mock())

    assert display_mock.set_caption.called
    assert display_mock.set_mode.called
    assert init_mock.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.logging")
@patch("thegame.engine.Engine._main_loop")
def test_exception_in_main_loop_is_caught(main_loop_mock, logging_mock):

    with pytest.raises(ValueError):
        main_loop_mock.side_effect = ValueError

        game = Engine(Mock())
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

    game = Engine(Mock())
    Thread(target=kill_game, args=(game, event_get_mock)).start()

    game.start()

    # Nothing to assert on.


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", list)
@patch("thegame.engine.engine.pygame.event.get")
def test_quit_event_causes_stopping_to_be_set_to_false(event_get_mock):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    game = Engine(Mock())
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

    game = Engine(Mock())
    game.start()

    assert not game.running
    assert logging_mock.debug.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get")
@patch("thegame.engine.engine.pygame.key.get_pressed")
@patch("thegame.engine.Engine._handle_keystrokes")
def test_holding_down_character_only_counts_as_one_call(
    keystroke_handle_mock, key_pressed_mock, event_get_mock
):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    key_pressed_mock.return_value = generate_keystroke_list(["a"])

    game = Engine(Mock())
    game.start()

    keystroke_handle_mock.assert_called_once_with(["a"])


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.pygame.mouse.get_pos", lambda: (0, 0))
@patch("thegame.engine.engine.pygame.event.get")
def test_mouse_button_down_causes_mouse_coordinates_to_be_recorded(event_get_mock):
    event_get_mock.return_value = [
        DummyEvent(pygame.MOUSEBUTTONDOWN),
        DummyEvent(pygame.QUIT),
    ]

    game = Engine(Mock())
    game.start()

    assert game.mouse_down_pos == (0, 0)


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.pygame.mouse.get_pos", lambda: (0, 0))
@patch("thegame.engine.engine.pygame.event.get")
def test_mouse_button_up_causes_mouse_down_pos_to_be_unset(event_get_mock):
    event_get_mock.return_value = [
        DummyEvent(pygame.MOUSEBUTTONUP),
        DummyEvent(pygame.QUIT),
    ]

    game = Engine(Mock())
    game.mouse_down_pos = (1, 2)
    game.start()

    assert game.mouse_down_pos is None


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.pygame.mouse.get_pos", lambda: (0, 0))
@patch("thegame.engine.engine.pygame.event.get")
def test_mouse_button_up_calls_interaction_in_menu(event_get_mock):
    event_get_mock.return_value = [
        DummyEvent(pygame.MOUSEBUTTONDOWN),
        DummyEvent(pygame.MOUSEBUTTONUP),
        DummyEvent(pygame.QUIT),
    ]

    mock_interaction = Mock()
    menu = BaseMenu(Mock())
    menu.register_interactive_zone(0, 0, 0, 0, mock_interaction)
    game = BaseGame(menu)
    engine = Engine(game)

    engine.start()

    assert mock_interaction.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get", MagicMock())
@patch("thegame.engine.engine.pygame.key.get_pressed")
def test_arrow_keys_can_be_used_to_interact_with_a_menu(keypress_mock):

    up_arrow = chr(273)
    down_arrow = chr(274)

    keypress_mock.side_effect = [
        generate_keystroke_list([up_arrow]),
        generate_keystroke_list([]),
        generate_keystroke_list([up_arrow]),
        generate_keystroke_list([]),
        generate_keystroke_list([down_arrow]),
        generate_keystroke_list([]),
        generate_keystroke_list([down_arrow]),
        generate_keystroke_list([]),
        generate_keystroke_list(["\r"]),
        generate_keystroke_list([]),
    ]

    mock_interaction = Mock()
    menu = BaseMenu(Mock())
    menu.register_interactive_zone(0, 0, 0, 0, mock_interaction)
    menu.register_interactive_zone(1, 1, 1, 1, Mock())
    game = BaseGame(menu)
    engine = Engine(game)

    try:
        engine.start()
    except StopIteration:
        # When keypresses have run out, a StopIteration exception will be thrown by mock.
        # This exception will be used to tell when the necessary testing is done, and to
        # stop the game, hence, pass.
        pass

    assert game.active_menu.focused_zone == 0
    assert mock_interaction.called
