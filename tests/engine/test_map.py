import pytest

from tests.test_utils import generate_sheet, generate_valid_map
from thegame.engine import Map
from thegame.engine.game_objects import GameObject, PlayerControlledObject


@pytest.mark.parametrize(
    "foreground_sheet_valid, path_sheet_valid, background_sheet_valid, character_sheet_valid",
    [
        (False, True, True, True),
        (True, False, True, True),
        (True, True, False, True),
        (True, True, True, False),
    ],
)
def test_invalid_sheet_data_raises_exception(
    foreground_sheet_valid,
    path_sheet_valid,
    background_sheet_valid,
    character_sheet_valid,
):
    foreground_sheet = generate_sheet(foreground_sheet_valid)
    path_sheet = generate_sheet(path_sheet_valid)
    background_sheet = generate_sheet(background_sheet_valid)
    character_sheet = generate_sheet(character_sheet_valid)

    with pytest.raises(Map.InvalidObjectInSheetException):
        Map(foreground_sheet, path_sheet, background_sheet, character_sheet)


@pytest.mark.parametrize(
    "foreground_sheet_valid, path_sheet_valid, background_sheet_valid, character_sheet_valid",
    [
        (False, True, True, True),
        (True, False, True, True),
        (True, True, False, True),
        (True, True, True, False),
    ],
)
def test_invalid_sheet_type_raises_exception(
    foreground_sheet_valid,
    path_sheet_valid,
    background_sheet_valid,
    character_sheet_valid,
):
    foreground_sheet = generate_sheet(None, foreground_sheet_valid)
    path_sheet = generate_sheet(None, path_sheet_valid)
    background_sheet = generate_sheet(None, background_sheet_valid)
    character_sheet = generate_sheet(None, character_sheet_valid)

    with pytest.raises(ValueError):
        Map(foreground_sheet, path_sheet, background_sheet, character_sheet)


def test_tile_sheets_is_list_of_specific_sheets():

    foreground_sheet = generate_sheet(True)
    path_sheet = generate_sheet(True)
    background_sheet = generate_sheet(True)
    character_sheet = generate_sheet(True)
    test_map = Map(foreground_sheet, path_sheet, background_sheet, character_sheet)

    tiles = test_map.tile_sheets

    assert tiles[Map.FOREGROUND_SHEET_INDEX] == foreground_sheet
    assert tiles[Map.PATH_SHEET_INDEX] == path_sheet
    assert tiles[Map.CHARACTER_SHEET_INDEX] == character_sheet
    assert tiles[Map.BACKGROUND_SHEET_INDEX] == background_sheet


def test_register_warp_zone_correctly_adds_zone():

    test_map = generate_valid_map()

    test_map.register_warp_zone(0, 0, test_map, 0, 0)

    assert (0, 0, 0, 0, test_map, 0, 0) in test_map._warp_zones


@pytest.mark.parametrize("x_pos, y_pos, final_x, final_y", [(0, 0, 1, 1), (1, 1, 0, 0)])
def test_register_warp_zone_correctly_adds_large_zone(x_pos, y_pos, final_x, final_y):

    test_map = generate_valid_map()
    warp_map = generate_valid_map()

    test_map.register_warp_zone(
        x_pos, y_pos, warp_map, 0, 0, final_x_pos=final_x, final_y_pos=final_y
    )

    assert (0, 0, 1, 1, warp_map, 0, 0) in test_map._warp_zones


def test_registering_warp_zone_outside_warp_location_raises_exception():

    test_map = generate_valid_map()

    # Try to create a warp zone to 10, 10 in a 2x2 sheet.
    with pytest.raises(Map.InvalidWarpZoneLocationException):
        test_map.register_warp_zone(0, 0, test_map, 10, 10)


def test_swap_swaps_two_tiles():

    go1 = GameObject("sprite.png")
    go2 = GameObject("sprite.png")

    output_sheet = [[go1, go2]]
    test_map = Map(
        [[go2, go1]], [[go2, go1]], [[go2, go1]], [[go2, go1]], validate=False
    )

    test_map.swap((0, 0), (1, 0), Map.FOREGROUND_SHEET_INDEX, ignore_collision=True)
    test_map.swap((0, 0), (1, 0), Map.CHARACTER_SHEET_INDEX, ignore_collision=True)
    test_map.swap((0, 0), (1, 0), Map.PATH_SHEET_INDEX, ignore_collision=True)
    test_map.swap((0, 0), (1, 0), Map.BACKGROUND_SHEET_INDEX, ignore_collision=True)

    assert test_map.tile_sheets == (
        list(output_sheet),
        list(output_sheet),
        list(output_sheet),
        list(output_sheet),
    )


def test_player_controlled_objects_contains_all_player_controlled_objects_and_their_coordinates():
    pco1 = PlayerControlledObject("sprite.png")
    pco2 = PlayerControlledObject("sprite.png")

    test_map = Map([[pco1, pco2]], [[1, 2]], [[1, 2]], [[1, 2]], validate=False)

    player_controlled_objects = test_map.player_controlled_objects

    assert (pco1, 0, 0) in player_controlled_objects
    assert (pco2, 1, 0) in player_controlled_objects
    assert len(player_controlled_objects) == 2


def test_swap_done_on_sheet_less_than_0_raises_value_error():
    test_map = Map([[1, 2]], [[1, 2]], [[1, 2]], [[1, 2]], validate=False)

    with pytest.raises(ValueError):
        test_map.swap((0, 1), (0, 1), Map.FOREGROUND_SHEET_INDEX - 1)


def test_swap_done_on_sheet_greater_than_3_raises_value_error():
    test_map = Map([[1, 2]], [[1, 2]], [[1, 2]], [[1, 2]], validate=False)

    with pytest.raises(ValueError):
        test_map.swap((0, 1), (0, 1), Map.BACKGROUND_SHEET_INDEX + 1)


def test_collision_is_not_registered_when_ignore_collision_is_true_in_swap():
    pco1 = PlayerControlledObject("sprite.png", collides=True)
    pco2 = PlayerControlledObject("sprite.png", collides=True)
    test_map = Map([[pco1, pco2]], [[None, None]], [[None, None]], [[None, None]])

    test_map.swap(
        (1, 0), (0, 0), sheet=Map.FOREGROUND_SHEET_INDEX, ignore_collision=True
    )

    # Check that a swap did happen.
    assert test_map.tile_sheets[Map.FOREGROUND_SHEET_INDEX][0][0] is pco2
    assert test_map.tile_sheets[Map.FOREGROUND_SHEET_INDEX][0][1] is pco1


def test_collision_occurs_when_one_swap_would_be_off_left_of_screen():

    test_map = generate_valid_map()

    swapped = test_map.swap((-1, 0), (0, 0), sheet=0)

    assert not swapped


def test_collision_occurs_when_one_swap_would_be_off_top_of_screen():

    test_map = generate_valid_map()

    swapped = test_map.swap((0, -1), (0, 0), sheet=0)

    assert not swapped


def test_collision_occurs_when_one_swap_would_be_off_right_of_screen():

    test_map = generate_valid_map()  # Generates a 2z2

    swapped = test_map.swap((2, 0), (1, 0), sheet=0)

    assert not swapped


def test_collision_occurs_when_one_swap_would_be_bottom_right_of_screen():

    test_map = generate_valid_map()  # Generates a 2z2

    swapped = test_map.swap((0, 2), (0, 1), sheet=0)

    assert not swapped


def test_collision_occurs_with_collidable_objects_in_other_sheets():
    go = GameObject("sprite.png", collides=False)
    collision_go = GameObject("sprite.png", collides=True)

    test_map = Map([[go, None]], [[None, collision_go]], [[None, None]], [[None, None]])

    swapped = test_map.swap((0, 0), (1, 0), sheet=Map.FOREGROUND_SHEET_INDEX)

    assert not swapped


def test_collision_occurs_when_collidable_object_moves_into_non_collidable_in_different_sheet():
    go = GameObject("sprite.png", collides=False)
    collision_go = GameObject("sprite.png", collides=True)

    test_map = Map([[go, None]], [[None, collision_go]], [[None, None]], [[None, None]])

    swapped = test_map.swap((0, 0), (1, 0), sheet=Map.CHARACTER_SHEET_INDEX)

    assert not swapped


@pytest.mark.parametrize(
    "go1_collides, go2_collides",
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_collision_occurs_when_two_object_on_same_sheet_would_swap(
    go1_collides, go2_collides
):
    """ This test checks that if two objects, regardless of collision-ness, will collide
        if they are in the same sheet."""
    go1 = GameObject("sprite.png", collides=go1_collides)
    go2 = GameObject("sprite.png", collides=go2_collides)

    test_map = Map([[go1, go2]], [[None, None]], [[None, None]], [[None, None]])

    swapped = test_map.swap((0, 0), (1, 0), sheet=Map.FOREGROUND_SHEET_INDEX)

    assert not swapped


def test_swap_returns_true_when_no_collisions_occur():
    test_map = Map([[None, None]], [[None, None]], [[None, None]], [[None, None]])

    swapped = test_map.swap((0, 0), (1, 0), sheet=Map.FOREGROUND_SHEET_INDEX)

    assert swapped
