from thegame.engine.game_objects import GameObject


def test_initialize_game_object_with_animation_sets_it():

    go = GameObject("sprite.png", animation="animation.gif")

    assert go.sprite == "sprite.png"
    assert go.animation == "animation.gif"


def test_initialize_game_object_without_animation_set_it_to_none():

    go = GameObject("sprite.png")

    assert go.sprite == "sprite.png"
    assert go.animation is None
