from unittest.mock import Mock

import pytest

from thegame.engine.game_objects import GameObject


def test_initialize_game_object_with_animation_sets_it():

    go = GameObject("sprite.png", animation="animation.gif")

    assert go.sprite_location == "sprite.png"
    assert go.animation == "animation.gif"


def test_initialize_game_object_without_animation_set_it_to_none():

    go = GameObject("sprite.png")

    assert go.sprite_location == "sprite.png"
    assert go.animation is None


def test_clone_produces_object_with_same_sprite_info():

    go = GameObject("sprite.png")
    clone = go.clone()

    assert clone.sprite_location == go.sprite_location
    assert clone.animation == go.animation


def test_the_registered_sprite_can_be_loaded_and_unloaded():

    go = GameObject("sprite.png")
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock)

    assert go._loaded_sprite is sprite_mock

    go.deregister_loaded_sprite()

    assert go._loaded_sprite is None


def test_get_sprite_returns_sprite():

    go = GameObject("sprite.png")
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock)

    assert go.get_sprite() is sprite_mock


def test_get_sprite_on_spriteless_object_throws_value_error():

    go = GameObject("sprite.png")

    with pytest.raises(ValueError):
        go.get_sprite()


def test_set_sprite_position_sets_position_correctly():

    go = GameObject("sprite.png")
    sprite_mock = Mock()
    go.register_loaded_sprite(sprite_mock)

    go.set_sprite_position(pos_x=5, pos_y=4)

    assert sprite_mock.image.get_rect.called
    assert sprite_mock.rect.x == 5
    assert sprite_mock.rect.y == 4


def test_set_sprite_position_on_spriteless_object_throws_value_error():

    go = GameObject("sprite.png")

    with pytest.raises(ValueError):
        go.set_sprite_position(pos_x=5, pos_y=4)


def test_name_in_game_object_string_when_set():

    go = GameObject("sprite.png", name="Bob")

    assert "Bob" in str(go)


def test_game_object_type_name_in_string():

    go = GameObject("spring.png")

    assert type(go).__name__ in str(go)
