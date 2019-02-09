from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from tests.test_utils import generate_sheet, generate_valid_map, get_base_menu
from thegame.engine import BaseGame, Map
from thegame.engine.game_objects import GameObject, PlayerControlledObject


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
    assert len(game.maps) == 2


def test_register_menu_adds_new_menu_to_menus():
    base_menu = get_base_menu()
    test_menu = get_base_menu()

    game = BaseGame(main_menu=base_menu)
    game.register_menu("test menu", test_menu)

    assert game.menus["test menu"] is test_menu
    assert len(game.menus) == 2


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


@patch("pygame.event.post")
def test_shutdown_stops_the_game(event_post_mock):
    base_map = generate_valid_map()
    quit_event = pygame.event.Event(pygame.QUIT, dict=None)

    game = BaseGame(initial_map=base_map)
    game.shutdown()

    event_post_mock.assert_called_with(quit_event)


def test_open_menu_with_invalid_menu_name_raises_value_error():
    base_map = generate_valid_map()

    game = BaseGame(initial_map=base_map)

    with pytest.raises(ValueError):
        game.open_menu("test")


def test_open_menu_sets_the_menu():
    base_menu = get_base_menu()

    game = BaseGame(main_menu=base_menu)
    game.register_menu("menu", base_menu)

    game.open_menu("menu")

    assert game.active_menu is base_menu
    assert game.active_screen is base_menu


@patch("thegame.engine.base_game.BaseGame.unload_active_map")
def test_open_menu_unloads_current_map(unload_map_mock):
    base_map = generate_valid_map()
    base_menu = get_base_menu()

    game = BaseGame(initial_map=base_map)
    game.register_menu("menu", base_menu)

    game.open_menu("menu")

    assert unload_map_mock.called


def test_unload_active_map_sets_game_object_sprites_to_none():
    go = GameObject({"sprite": "sprite.png"})

    base_sheet = [[go.clone(), go.clone()], [go.clone(), go.clone()]]

    base_map = Map(
        list(base_sheet), list(base_sheet), list(base_sheet), list(base_sheet)
    )

    game = BaseGame(initial_map=base_map)

    game.unload_active_map()

    with pytest.raises(AttributeError):
        base_sheet[0][0].get_sprite()
        base_sheet[0][1].get_sprite()
        base_sheet[1][0].get_sprite()
        base_sheet[1][1].get_sprite()


def test_load_active_maps_sets_game_object_sprites():
    go = GameObject({"sprite": "sprite.png"})
    base_sheet = [[go.clone(), go.clone()], [go.clone(), go.clone()]]
    base_map = Map(
        list(base_sheet), list(base_sheet), list(base_sheet), list(base_sheet)
    )

    sprite_mock = Mock()
    game = BaseGame(initial_map=base_map)
    game.object_images["sprite.png"] = sprite_mock

    # Usually the engine handles calling this, but there is no
    # engine running so we need to call this manually.
    game.load_active_map()

    assert base_sheet[0][0].get_sprite().image is sprite_mock
    assert base_sheet[0][1].get_sprite().image is sprite_mock
    assert base_sheet[1][0].get_sprite().image is sprite_mock
    assert base_sheet[1][1].get_sprite().image is sprite_mock


def test_register_player_controlled_object_correctly_registers():
    pco = PlayerControlledObject({"sprite": "sprite.png"})

    game = BaseGame(initial_map=generate_valid_map())

    game.register_player_controlled_object(pco, 1, 2)

    assert game.player_controlled_objects[pco] == (1, 2)
    assert len(game.player_controlled_objects) == 1


@patch("pygame.sprite.Sprite", MagicMock())
def test_change_map_loads_new_player_controlled_objects_and_unloads_previous_ones():

    pco1 = PlayerControlledObject({"sprite": "sprite.png"})
    pco2 = PlayerControlledObject({"sprite": "sprite.png"})
    pco3 = PlayerControlledObject({"sprite": "sprite.png"})
    pco4 = PlayerControlledObject({"sprite": "sprite.png"})

    go_mock = MagicMock()
    go_mock.sprite_locations = {"sprite": "sprite.png"}

    test_map = Map(
        [[pco1, pco2]],
        [[go_mock, go_mock]],
        [[go_mock, go_mock]],
        [[go_mock, go_mock]],
        validate=False,
    )
    alt_map = Map(
        [[pco3, pco4]],
        [[go_mock, go_mock]],
        [[go_mock, go_mock]],
        [[go_mock, go_mock]],
        validate=False,
    )

    game = BaseGame(initial_map=test_map)
    game.object_images["sprite.png"] = Mock()  # Setup a mock to load the image as.
    game.register_map("alt", alt_map)

    game.change_map("alt")

    assert pco1 not in game.player_controlled_objects
    assert pco2 not in game.player_controlled_objects
    assert game.player_controlled_objects[pco3] == (0, 0)
    assert game.player_controlled_objects[pco4] == (1, 0)
    assert len(game.player_controlled_objects) == 2


def test_clear_player_controlled_objects_clears_them():

    game = BaseGame(initial_map=generate_valid_map())
    game.register_player_controlled_object(
        PlayerControlledObject({"sprite": "sprite.png"}), 0, 0
    )
    game.register_player_controlled_object(
        PlayerControlledObject({"sprite": "sprite.png"}), 0, 1
    )

    game.clear_player_controlled_objects()

    assert game.player_controlled_objects == {}


def test_load_player_controlled_objects_loads_them():

    game = BaseGame(initial_map=generate_valid_map())
    pco1 = PlayerControlledObject({"sprite": "sprite.png"})
    pco2 = PlayerControlledObject({"sprite": "sprite.png"})
    load_map = Map([[pco1, pco2]], [[0, 0]], [[0, 0]], [[0, 0]], validate=False)

    game.load_player_controlled_objects(load_map)

    assert pco1 in game.player_controlled_objects
    assert pco2 in game.player_controlled_objects
    assert game.player_controlled_objects[pco1] == (0, 0)
    assert game.player_controlled_objects[pco2] == (1, 0)
