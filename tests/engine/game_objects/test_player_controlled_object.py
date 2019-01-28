from unittest.mock import Mock

import pytest

from thegame.engine.game_objects import PlayerControlledObject


def test_base_player_controlled_object_player_interaction_raises_not_implemented_error():
    pco = PlayerControlledObject("sprite")

    with pytest.raises(NotImplementedError):
        pco.player_interaction([], Mock())
