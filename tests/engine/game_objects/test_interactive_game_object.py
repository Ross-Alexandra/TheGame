from unittest.mock import Mock

import pytest

from thegame.engine.game_objects import InteractiveGameObject


def test_instantiating_default_interactive_game_object_raises_not_implemented_error():

    igo = InteractiveGameObject("sprite.txt")

    with pytest.raises(NotImplementedError):
        igo.interact(Mock())
