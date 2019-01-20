""" A module containing basic utilities used in multiple test files."""
from unittest.mock import Mock

import thegame.engine as engine

UP_ARROW_CHAR = chr(273)
DOWN_ARROW_CHAR = chr(274)


class DummyEvent:
    """ An event that can be used to simulate a real event for testing."""

    def __init__(self, event_type):
        self.type = event_type


def get_base_menu():
    """ Get an initialized menu. """

    # TODO: Once actual image loading has been implemented
    # this mock should probably have some return values.
    return engine.BaseMenu(Mock())


def generate_sheet(data_is_valid, contents_are_valid=True):
    """ Generate a sheet based on arguments.

        Args:
            data_is_valid: If this is set to True or None, return a map with
                            Nones in it (a valid data type.)
                            If this is set to False, then return a map with
                            1s in it (an invalid data type.)

            contents_are_valid: If this is False, then return a
                                1D list (invalid as a sheet must be 3D)
                                If this is True, then fall back on data_is_valid.
    """

    if not contents_are_valid:
        return [None, None, None, None]

    if data_is_valid or data_is_valid is None:
        return [[None, None], [None, None]]
    else:
        return [[1, 1], [1, 1]]


def generate_valid_map():
    """ Generate a map with 4 valid 2x2 sheets. """
    foreground_sheet = generate_sheet(True)
    path_sheet = generate_sheet(True)
    background_sheet = generate_sheet(True)
    character_sheet = generate_sheet(True)
    return engine.Map(foreground_sheet, path_sheet, background_sheet, character_sheet)
