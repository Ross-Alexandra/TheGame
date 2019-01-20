import pytest

from tests.test_utils import generate_valid_map, get_base_menu
from thegame.engine import BaseGame


def test_creating_game_without_main_screen_or_menu_throws_error():
    with pytest.raises(SyntaxError):
        BaseGame()


def test_creating_game_with_main_menu_sets_active_screen_and_menu():
    menu = get_base_menu()

    game = BaseGame(main_menu=menu)

    assert game.active_screen is menu
    assert game.active_menu is menu
    assert game.maps == {}


def test_creating_game_with_initial_map_sets_active_screen_and_maps():
    test_map = generate_valid_map()

    game = BaseGame(initial_map=test_map, initial_map_name="test map")

    assert game.active_screen is test_map
    assert game.active_menu is None
    assert game.maps["test map"] is test_map


def test_register_map_adds_new_map_to_maps():
    base_map = generate_valid_map()
    test_map = generate_valid_map()

    game = BaseGame(initial_map=base_map, initial_map_name="base map")
    game.register_map("test map", test_map)

    assert game.maps["test map"] is test_map


def test_change_map_sets_active_screen():
    base_map = generate_valid_map()
    test_map = generate_valid_map()

    game = BaseGame(initial_map=base_map, initial_map_name="bae map")
    game.register_map("test map", test_map)
    game.change_map("test map")

    assert game.active_screen is test_map


def test_change_map_to_invalid_map_throws_exception():
    base_map = generate_valid_map()

    game = BaseGame(initial_map=base_map)

    with pytest.raises(ValueError):
        game.change_map("Invalid map name.")
