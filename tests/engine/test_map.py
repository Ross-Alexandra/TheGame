from unittest.mock import Mock

import pytest

from thegame.engine import Map
from thegame.engine.game_objects import GameObject


def generate_sheet(data_is_valid, contents_are_valid=True):
    if not contents_are_valid:
        return [None, None, None, None]

    if data_is_valid or data_is_valid is None:
        return [[None, None], [None, None]]
    else:
        return [[1, 1], [1, 1]]


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


@pytest.mark.parametrize("x_pos, y_pos, final_x, final_y", [(0, 0, 1, 0), (1, 0, 0, 0)])
def test_register_warp_zone_correctly_adds_zone(x_pos, y_pos, final_x, final_y):

    foreground_sheet = generate_sheet(True)
    path_sheet = generate_sheet(True)
    background_sheet = generate_sheet(True)
    character_sheet = generate_sheet(True)
    test_map = Map(foreground_sheet, path_sheet, background_sheet, character_sheet)
    warp_map = Map(foreground_sheet, path_sheet, background_sheet, character_sheet)

    test_map.register_warp_zone(
        x_pos, y_pos, warp_map, 0, 0, final_x_pos=final_x, final_y_pos=final_y
    )

    assert (0, 0, 1, 0, warp_map, 0, 0) in test_map._warp_zones


def test_registering_warp_zone_outside_warp_location_raises_exception():
    foreground_sheet = generate_sheet(True)
    path_sheet = generate_sheet(True)
    background_sheet = generate_sheet(True)
    character_sheet = generate_sheet(True)
    test_map = Map(foreground_sheet, path_sheet, background_sheet, character_sheet)

    # Try to create a warp zone to 10, 10 in a 2x2 sheet.
    with pytest.raises(Map.InvalidWarpZoneLocationException):
        test_map.register_warp_zone(0, 0, test_map, 10, 10)
