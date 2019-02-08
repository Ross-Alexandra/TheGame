from unittest.mock import Mock

import pytest

from thegame.engine.game_objects import GameObject


def test_initialize_game_object_with_animation_sets_it():

    go = GameObject({"sprite": "sprite.png"}, animation="animation.gif")

    assert go.get_active_sprite_location() == "sprite.png"
    assert go.animation == "animation.gif"


def test_initialize_game_object_without_animation_set_it_to_none():

    go = GameObject({"sprite": "sprite.png"})

    assert go.get_active_sprite_location() == "sprite.png"
    assert go.animation is None


def test_clone_produces_object_with_same_sprite_info():

    go = GameObject({"sprite": "sprite.png"})
    clone = go.clone()

    assert clone.get_sprite_locations() == go.get_sprite_locations()
    assert clone.animation == go.animation


def test_clone_produces_object_with_same_sprite_info_multiple():

    go = GameObject(
        {"sprite1": "sprite1.png", "sprite2": "sprite2.png"}, initial_sprite="sprite2"
    )
    clone = go.clone()

    assert clone.get_sprite_locations() == go.get_sprite_locations()
    assert clone.active_sprite == go.active_sprite
    assert clone.animation == go.animation


def test_the_registered_sprite_can_be_loaded():

    go = GameObject({"sprite": "sprite.png"})
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock, "sprite.png")

    assert go.get_sprite() is sprite_mock


def test_the_registered_spite_can_be_unloaded():

    go = GameObject({"sprite": "sprite.png"})
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock, "sprite.png")
    go.deregister_loaded_sprites()
    with pytest.raises(AttributeError):
        go.get_sprite()


def test_get_sprite_returns_sprite():

    go = GameObject({"sprite": "sprite.png"})
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock, "sprite.png")

    assert go.get_sprite() is sprite_mock


def test_get_sprite_with_no_active_sprite_throws_attribute_error():

    go = GameObject({"sprite": "sprite.png"})
    go.active_sprite = None

    with pytest.raises(AttributeError):
        go.get_sprite()


def test_get_sprite_throws_error_on_empty_loaded_sprite_dict():

    go = GameObject({})

    with pytest.raises(AttributeError):
        go.get_sprite()


def test_set_sprite_position_sets_position_correctly():

    go = GameObject({"sprite": "sprite.png"})
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock, "sprite.png")

    go.set_sprite_position(pos_x=5, pos_y=4)

    assert sprite_mock.image.get_rect.called
    assert sprite_mock.rect.x == 5
    assert sprite_mock.rect.y == 4


def test_set_sprite_position_on_spriteless_object_throws_value_error():

    go = GameObject({"sprite": "sprite.png"})

    with pytest.raises(AttributeError):
        go.set_sprite_position(pos_x=5, pos_y=4)


def test_name_in_game_object_string_when_set():

    go = GameObject({"sprite": "sprite.png"}, name="Bob")

    assert "Bob" in str(go)


def test_game_object_type_name_in_string():

    go = GameObject({"sprite": "sprite.png"})

    assert type(go).__name__ in str(go)


def test_add_sprite_location():

    go = GameObject({"sprite": "sprite.png"})

    go.add_sprite_location("new_sprite", "new_sprite.png")

    assert "new_sprite" in go.sprite_locations
    assert go.sprite_locations["new_sprite"] == "new_sprite.png"


def test_get_active_sprite_location():

    go = GameObject({"sprite": "sprite.png"})

    assert go.get_active_sprite_location() == "sprite.png"


def test_get_sprite_locations():

    go = GameObject(
        {"sprite1": "sprite1.png", "sprite2": "sprite2.png"}, initial_sprite="sprite2"
    )

    assert go.get_sprite_locations() == ["sprite1.png", "sprite2.png"]
