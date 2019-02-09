from threading import Thread
from unittest.mock import MagicMock, Mock, call, patch

import pygame
import pytest

from tests.test_utils import (
    DOWN_ARROW_CHAR,
    UP_ARROW_CHAR,
    DummyEvent,
    generate_valid_map,
)
from thegame.engine import BaseGame, BaseMenu, Engine, Map
from thegame.engine.game_objects import GameObject, PlayerControlledObject


def generate_keypress_pattern(characters, convert_to_keystroke=True):
    """ Returns a list of keystroke lists which can be fed into a
        mock.side_effect to generate a sequence of key presses.
        Ex) for a, ab, a, b

        generate_keypress_patterns(["a", "ab", "a", "b"])

    """

    keypresses = []

    for character in characters:
        if character is None:
            keypresses.append(generate_keystroke_list([]))
        else:
            keypresses.append(generate_keystroke_list([character]))
            if convert_to_keystroke:
                keypresses.append(generate_keystroke_list([]))

    return keypresses


def generate_keystroke_list(characters_pressed):
    key_presses = [0 for _ in range(355)]

    for key in characters_pressed:
        key_presses[ord(key)] = True

    return key_presses


@patch("thegame.engine.engine.pygame.init")
@patch("thegame.engine.engine.pygame.display")
@patch("thegame.engine.engine.pygame.quit", Mock())
@patch("thegame.engine.engine.Engine._main_loop", Mock())
def test_engine_start_initializes_game_window(display_mock, init_mock):

    Engine(MagicMock()).start()

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

        game = Engine(MagicMock())
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

    game = Engine(MagicMock())
    Thread(target=kill_game, args=(game, event_get_mock)).start()

    game.start()

    # Nothing to assert on.


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", list)
@patch("thegame.engine.engine.pygame.event.get")
def test_quit_event_causes_stopping_to_be_set_to_false(event_get_mock):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    game = Engine(MagicMock())
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

    game = Engine(MagicMock())
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

    game = Engine(MagicMock())
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

    game = Engine(MagicMock())
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

    game = Engine(MagicMock())
    game.mouse_down_pos = (1, 2)
    game.start()

    assert game.mouse_down_pos is None


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.pygame.image", MagicMock())
@patch("thegame.engine.engine.pygame.mouse.get_pos", lambda: (0, 0))
@patch("thegame.engine.engine.pygame.event.get")
def test_mouse_button_up_calls_interaction_in_menu(event_get_mock):
    event_get_mock.return_value = [
        DummyEvent(pygame.MOUSEBUTTONDOWN),
        DummyEvent(pygame.MOUSEBUTTONUP),
        DummyEvent(pygame.QUIT),
    ]

    mock_interaction = Mock()
    menu = BaseMenu(MagicMock())
    menu.register_interactive_zone(0, 0, 0, 0, mock_interaction)
    game = BaseGame(menu)
    engine = Engine(game)

    engine.start()

    assert mock_interaction.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get", MagicMock())
@patch("thegame.engine.engine.pygame.image", MagicMock())
@patch("thegame.engine.engine.pygame.key.get_pressed")
@pytest.mark.parametrize(
    "keystroke_pattern, interaction_index",
    [
        ([UP_ARROW_CHAR, "\r"], 1),
        ([DOWN_ARROW_CHAR, "\r"], 0),
        ([UP_ARROW_CHAR, DOWN_ARROW_CHAR, "\r"], 0),
        ([DOWN_ARROW_CHAR, UP_ARROW_CHAR, "\r"], 1),
    ],
)
def test_arrow_keys_can_be_used_to_interact_with_a_menu(
    keypress_mock, keystroke_pattern, interaction_index
):

    keypress_mock.side_effect = generate_keypress_pattern(keystroke_pattern)

    mock_interaction = Mock()
    menu = BaseMenu(MagicMock())

    menu.register_interactive_zone(
        0, 0, 0, 0, Mock() if interaction_index == 1 else mock_interaction
    )
    menu.register_interactive_zone(
        1, 1, 1, 1, Mock() if interaction_index == 0 else mock_interaction
    )

    game = BaseGame(menu)
    engine = Engine(game)

    try:
        engine.start()
    except StopIteration:
        # When keypresses have run out, a StopIteration exception will be thrown by mock.
        # This exception will be used to tell when the necessary testing is done, and to
        # stop the game, hence, pass.
        pass

    assert game.active_menu.focused_zone == interaction_index
    assert mock_interaction.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.Engine._handle_event")
@patch("thegame.engine.engine.pygame.event.get")
def test_handle_event_raises_exception_causes_game_to_stop(
    event_get_mock, event_handle_mock
):

    event_get_mock.return_value = [DummyEvent(pygame.MOUSEBUTTONDOWN)]

    engine = Engine(MagicMock())
    event_handle_mock.side_effect = Mock(spec=ValueError)

    engine.start()

    assert not engine.running


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get", MagicMock())
@patch("thegame.engine.engine.pygame.key.get_pressed")
@patch("thegame.engine.engine.Engine._handle_keystrokes")
@pytest.mark.parametrize(
    "keystroke_pattern",
    [
        (["w", "w", "w", "w"]),
        (["a", "a", "s", "s"]),
        (["d", "s", None, "s", "d"]),
        (["w", None, "s", None, "a", None, "d", "d", "d"]),
    ],
)
def test_held_keys_are_not_handled_as_multiple_keystrokes(
    handle_keypress_mock, keypress_mock, keystroke_pattern
):

    keypress_mock.side_effect = generate_keypress_pattern(
        keystroke_pattern, convert_to_keystroke=False
    )

    engine = Engine(MagicMock())

    try:
        engine.start()
    except StopIteration:
        # When keypresses have run out, a StopIteration exception will be thrown by mock.
        # This exception will be used to tell when the necessary testing is done, and to
        # stop the game, hence, pass.
        pass

    call_args = handle_keypress_mock.call_args_list
    presses = []
    calls = []

    print(call_args)

    # Check that each call had the previous call's
    # keystroke(s), as well as its own keystroke.
    for index, keystroke in enumerate(keystroke_pattern):
        presses.append(keystroke)
        if keystroke is None:
            presses.clear()

        # Remove duplicates, as these shouldn't exist in
        # the actual calls.
        current_presses_call = call(list(set(presses)))

        # If this call isn't the same as the last one.
        if len(calls) > 0 and calls[-1] != current_presses_call:
            calls.append(current_presses_call)

    handle_keypress_mock.assert_has_calls(calls, any_order=True)


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.Engine._handle_keystrokes", Mock())
@patch("thegame.engine.engine.pygame.event.get")
@patch("thegame.engine.base_game.BaseGame.load_active_map")
def test_loading_a_game_with_no_menu_loads_the_active_map(
    load_map_mock, event_get_mock
):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    game_map = generate_valid_map()
    game = BaseGame(initial_map=game_map)
    engine = Engine(game)

    engine.start()

    assert load_map_mock.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.Engine._handle_keystrokes", Mock())
@patch("pygame.image.load")
@patch("thegame.engine.engine.pygame.event.get")
@patch("pygame.sprite.Group.add")
def test_onscreen_sprites_are_correctly_added(
    sprite_group_mock, event_get_mock, image_load_mock
):
    event_get_mock.return_value = [DummyEvent(pygame.QUIT)]

    sprite_mock = Mock(name="sprite_mock")
    convert_alpha_mock = Mock()
    convert_alpha_mock.convert_alpha.return_value = sprite_mock

    image_load_mock.return_value = convert_alpha_mock

    go1 = GameObject({"sprite": "sprite.png"})
    go2 = GameObject({"sprite": "sprite.png"})
    go3 = GameObject({"sprite": "sprite.png"})

    sheet = [
        [go1.clone(), go2.clone(), go3.clone()],
        [go3.clone(), go1.clone(), go2.clone()],
        [go2.clone(), go3.clone(), go1.clone()],
    ]

    game_map = Map(list(sheet), list(sheet), list(sheet), list(sheet), validate=False)

    game = BaseGame(
        initial_map=game_map, camera_width=3, camera_height=3, camera_x=1, camera_y=1
    )
    engine = Engine(game)
    engine.start()

    call_args = sprite_group_mock.call_args

    # Ignore empty calls.
    assert all(
        call_arg[0].image is sprite_mock for call_arg in call_args if len(call_arg) >= 1
    )


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("thegame.engine.engine.pygame.event.get", MagicMock())
@patch("pygame.image.load", MagicMock())
@patch("thegame.engine.engine.pygame.key.get_pressed")
def test_handle_keystrokes_calls_each_player_controlled_objects_interaction(
    keypress_mock
):
    pco1 = MagicMock(spec=PlayerControlledObject)
    pco2 = MagicMock(spec=PlayerControlledObject)
    pco1.sprite_location = "sprite.png"
    pco2.sprite_location = "sprite.png"

    keypress_mock.side_effect = generate_keypress_pattern(
        ["w"], convert_to_keystroke=True
    )

    test_map = Map(
        [[pco1, pco2]],
        [[MagicMock(), MagicMock()]],
        [[MagicMock(), MagicMock()]],
        [[MagicMock(), MagicMock()]],
        validate=False,
    )
    game = BaseGame(
        initial_map=test_map, camera_width=3, camera_height=1, camera_x=1, camera_y=1
    )
    engine = Engine(game=game)

    try:
        engine.start()
    except StopIteration:
        # When keypresses have run out, a StopIteration exception will be thrown by mock.
        # This exception will be used to tell when the necessary testing is done, and to
        # stop the game, hence, pass.
        pass

    assert pco1.player_interaction.called
    assert pco2.player_interaction.called


@patch("thegame.engine.engine.pygame.init", Mock())
@patch("thegame.engine.engine.pygame.display", Mock())
@patch("pygame.image.load", MagicMock())
@patch("thegame.engine.engine.pygame.key.get_pressed", MagicMock())
@patch("thegame.engine.engine.pygame.event.get")
def test_initializing_engine_with_game_loads_player_controlled_objects(event_queue):
    pco1 = PlayerControlledObject({"sprite": "sprite.png"})
    pco2 = PlayerControlledObject({"sprite": "sprite.png"})

    test_map = Map(
        [[pco1, pco2]],
        [[MagicMock(), MagicMock()]],
        [[MagicMock(), MagicMock()]],
        [[MagicMock(), MagicMock()]],
        validate=False,
    )
    game = BaseGame(
        initial_map=test_map, camera_width=3, camera_height=1, camera_x=1, camera_y=1
    )
    engine = Engine(game=game)

    event_queue.return_value = [DummyEvent(pygame.QUIT)]

    try:
        engine.start()
    except StopIteration:
        # When keypresses have run out, a StopIteration exception will be thrown by mock.
        # This exception will be used to tell when the necessary testing is done, and to
        # stop the game, hence, pass.
        pass

    assert pco1 in engine.context.player_controlled_objects
    assert pco2 in engine.context.player_controlled_objects
    assert engine.context.player_controlled_objects[pco1] == (0, 0)
    assert engine.context.player_controlled_objects[pco2] == (1, 0)
