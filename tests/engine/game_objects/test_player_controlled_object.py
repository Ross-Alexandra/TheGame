from unittest.mock import MagicMock, Mock, patch

import pytest

from thegame.engine import BaseGame, Map
from thegame.engine.game_objects import (
    InteractiveGameObject,
    PlayerCharacter,
    PlayerControlledObject,
)


def test_base_player_controlled_object_player_interaction_raises_not_implemented_error():
    pco = PlayerControlledObject({"sprite": "sprite.png"})

    with pytest.raises(NotImplementedError):
        pco.player_interaction([], Mock())


@pytest.mark.parametrize(
    "up, down, left, right, initial_pos, final_pos",
    [
        (False, False, False, True, (1, 1), (2, 1)),
        (False, False, True, False, (1, 1), (0, 1)),
        (False, False, True, True, (1, 1), (0, 1)),
        (False, True, False, False, (1, 1), (1, 2)),
        (False, True, False, True, (1, 1), (1, 2)),
        (False, True, True, False, (1, 1), (1, 2)),
        (False, True, True, True, (1, 1), (1, 2)),
        (True, False, False, False, (1, 1), (1, 0)),
        (True, False, False, True, (1, 1), (1, 0)),
        (True, False, True, False, (1, 1), (1, 0)),
        (True, False, True, True, (1, 1), (1, 0)),
        (True, True, False, False, (1, 1), (1, 0)),
        (True, True, False, True, (1, 1), (1, 0)),
        (True, True, True, False, (1, 1), (1, 0)),
        (True, True, True, True, (1, 1), (1, 0)),
    ],
)
def test_player_character_move_moves_as_documented(
    up, down, left, right, initial_pos, final_pos
):
    """
    Documentation from the class:

        "Going up always takes priority, going up or down takes priority
        over going left and right, and going left takes priority over going right.
        This means that if up and down, then the PC will move up; if up and
        left, then the PC will move up; if down and right, then the PC will
        move down; and if left and right, the PC will move left."
    """
    pc = PlayerCharacter(
        sprite_locations={
            "PC_up": "thegame/resources/PC_up.png",
            "PC_left": "thegame/resources/PC_left.png",
            "PC_down": "thegame/resources/PC_down.png",
            "PC_right": "thegame/resources/PC_right.png",
        }
    )

    game = BaseGame(MagicMock())
    game.register_player_controlled_object(pc, *initial_pos)

    pc.move(game, up, down, left, right)

    assert game.player_controlled_objects[pc] == final_pos


@patch("logging.warning")
def test_player_character_move_with_all_false_logs_warning(warning_mock):
    pc = PlayerCharacter({"sprite": "sprite.png"})

    pc.move(MagicMock(), False, False, False, False)

    assert warning_mock.called


@patch("thegame.engine.game_objects.character_object.PlayerCharacter.move")
@pytest.mark.parametrize(
    "keystrokes",
    [
        ["a"],
        ["w"],
        ["s"],
        ["d"],
        ["a", "w"],
        ["a", "s"],
        ["a", "d"],
        ["w", "s"],
        ["w", "d"],
        ["s", "d"],
        ["a", "s", "w"],
        ["w", "s", "d"],
        ["w", "a", "s", "d"],
    ],
)
def test_player_character_player_interaction_calls_move(move_mock, keystrokes):
    pc = PlayerCharacter({"sprite": "sprite.png"})

    pc.player_interaction(keystrokes, MagicMock())

    assert move_mock.called


@patch("thegame.engine.game_objects.character_object.PlayerCharacter.move")
def test_player_character_player_interaction_doesnt_call_move_when_no_correct_letters(
    move_mock
):
    keystrokes = {chr(i) for i in range(128)}
    keystrokes -= {"w", "a", "s", "d"}
    pc = PlayerCharacter({"sprite": "sprite.png"})

    pc.player_interaction(keystrokes, MagicMock())

    assert not move_mock.called


def test_player_character_facing_east_can_interact_with_igos():
    igo = Mock(spec=InteractiveGameObject)
    pc = PlayerCharacter(
        sprite_locations={"sprite": "sprite.png"}, facing_direction=PlayerCharacter.EAST
    )

    # Create a map of 2x1 sheets as we only need to look east.
    character_sheet = [[pc, igo]]
    sheet = [[None, None]]

    keystrokes = ["\r"]
    test_map = Map(sheet, character_sheet, sheet, sheet)
    game = BaseGame(initial_map=test_map)
    game.register_player_controlled_object(pc, 0, 0)

    pc.player_interaction(keystrokes, game)

    assert igo.interact.called


def test_player_character_facing_west_can_interact_with_igos():
    igo = Mock(spec=InteractiveGameObject)
    pc = PlayerCharacter(
        sprite_locations={"sprite": "sprite.png"}, facing_direction=PlayerCharacter.WEST
    )

    # Create a map of 2x1 sheets as we only need to look west.
    character_sheet = [[igo, pc]]
    sheet = [[None, None]]

    keystrokes = ["\r"]
    test_map = Map(sheet, character_sheet, sheet, sheet)
    game = BaseGame(initial_map=test_map)
    game.register_player_controlled_object(pc, 1, 0)

    pc.player_interaction(keystrokes, game)

    assert igo.interact.called


def test_player_character_facing_north_can_interact_with_igos():
    igo = Mock(spec=InteractiveGameObject)
    pc = PlayerCharacter(
        sprite_locations={"sprite": "sprite.png"},
        facing_direction=PlayerCharacter.NORTH,
    )

    # Create a map of 1x2 sheets as we only need to look north.
    character_sheet = [[igo], [pc]]
    sheet = [[None], [None]]

    keystrokes = ["\r"]
    test_map = Map(sheet, character_sheet, sheet, sheet)
    game = BaseGame(initial_map=test_map)
    game.register_player_controlled_object(pc, 0, 1)

    pc.player_interaction(keystrokes, game)

    assert igo.interact.called


def test_player_character_facing_south_can_interact_with_igos():
    igo = Mock(spec=InteractiveGameObject)
    pc = PlayerCharacter(
        sprite_locations={"sprite": "sprite.png"},
        facing_direction=PlayerCharacter.SOUTH,
    )

    # Create a map of 1x2 sheets as we only need to look south.
    character_sheet = [[pc], [igo]]
    sheet = [[None], [None]]

    keystrokes = ["\r"]
    test_map = Map(sheet, character_sheet, sheet, sheet)
    game = BaseGame(initial_map=test_map)
    game.register_player_controlled_object(pc, 0, 0)

    pc.player_interaction(keystrokes, game)

    assert igo.interact.called


def test_player_character_facing_invalid_direction_raises_attribute_error_when_interacting():
    pc = PlayerCharacter(sprite_locations={"sprite": "sprite.png"}, facing_direction=-1)

    with pytest.raises(AttributeError):
        pc.player_interaction(["\r"], MagicMock())


def test_player_character_interacts_with_topmost_igo():
    igo = Mock(spec=InteractiveGameObject)
    igo2 = Mock(spec=InteractiveGameObject)
    pc = PlayerCharacter(
        sprite_locations={"sprite": "sprite.png"},
        facing_direction=PlayerCharacter.SOUTH,
    )

    # Create a map of 1x2 sheets as we only need to look south.
    foreground_sheet = [[None], [igo]]

    character_sheet = [[pc], [igo2]]
    sheet = [[None], [igo2]]

    keystrokes = ["\r"]
    test_map = Map(foreground_sheet, character_sheet, sheet, sheet)
    game = BaseGame(initial_map=test_map)
    game.register_player_controlled_object(pc, 0, 0)

    pc.player_interaction(keystrokes, game)

    assert igo.interact.called
    assert not igo2.interact.called
