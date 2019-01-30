from unittest.mock import MagicMock, Mock, patch

import pytest

from thegame.engine import BaseGame
from thegame.engine.game_objects import PlayerCharacter, PlayerControlledObject


def test_base_player_controlled_object_player_interaction_raises_not_implemented_error():
    pco = PlayerControlledObject("sprite")

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
    pc = PlayerCharacter("sprite.png")

    game = BaseGame(MagicMock())
    game.register_player_controlled_object(pc, *initial_pos)

    pc.move(game, up, down, left, right)

    assert game.player_controlled_objects[pc] == final_pos


@patch("logging.warning")
def test_player_character_move_with_all_false_logs_warning(warning_mock):
    pc = PlayerCharacter("sprite.png")

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
    pc = PlayerCharacter("sprite.png")

    pc.player_interaction(keystrokes, MagicMock())

    assert move_mock.called


@patch("thegame.engine.game_objects.character_object.PlayerCharacter.move")
def test_player_character_player_interaction_doesnt_call_move_when_no_correct_letters(
    move_mock
):
    keystrokes = {chr(i) for i in range(128)}
    keystrokes -= {"w", "a", "s", "d"}
    pc = PlayerCharacter("sprite.png")

    pc.player_interaction(keystrokes, MagicMock())

    assert not move_mock.called
