from thegame.engine.game_objects.game_object import GameObject


class Map:
    """ An object representing a location in the game. A map is made up of 4 "sheets".
        The sheets are used to draw out the map by the game engine layer by layer.
        They're drawn in the following order:
            Background,
            Paths,
            Characters
            Foreground.

        If two objects overlap, then the last to be drawn will take priority. Ie, if a Path and
        Character overlap, then the Character will be drawn on top of the Path (any opaque pixels
        in a later-drawn object will be colour as a before-drawn object.

        Note, any object on the foreground layer will be impassible."""

    # Define the locations in the tile_sheets
    # tuple of each sheet.
    FOREGROUND_SHEET_INDEX = 0
    CHARACTER_SHEET_INDEX = 1
    PATH_SHEET_INDEX = 2
    BACKGROUND_SHEET_INDEX = 3

    # Define the locations of each parameter in the
    # _warp_zones tuple.
    WARP_ZONE_INITIAL_X_POSITION = 0
    WARP_ZONE_INITIAL_Y_POSITION = 1
    WARP_ZONE_FINAL_X_POSITION = 2
    WARP_ZONE_FINAL_Y_POSITION = 3
    WARP_ZONE_LOCATION = 4

    def __init__(
        self,
        foreground_sheet,
        path_sheet,
        background_sheet,
        character_sheet,
        validate=True,
    ):

        if validate:
            if not all(
                isinstance(o, GameObject) or o is None for o in foreground_sheet
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject found in object sheet."
                )
            elif not all(isinstance(o, GameObject) or o is None for o in path_sheet):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject found in path sheet."
                )
            elif not all(
                isinstance(o, GameObject) or o is None for o in background_sheet
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject found in background sheet."
                )
            elif not all(
                isinstance(o, GameObject) or o is None for o in character_sheet
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject found in character sheet."
                )

        self.foreground_sheet = foreground_sheet
        self.path_sheet = path_sheet
        self.background_sheet = background_sheet
        self.character_sheet = character_sheet

        self._warp_zones = []

    @property
    def tile_sheets(self):
        """ tile sheets is a tuple that the engine will
            use to update certain values depending on actions.

            The values of this tuple should reflect the following:
            game_sheets[0]: The foreground sheet.
            game_sheets[1]: The character sheet.
            game_sheets[2]: The paths sheet.
            game_sheets[3]: The background sheet.

            The object sheet is a sheet full objects implementing
            the GameObject class. etc. """

        return (
            self.foreground_sheet,
            self.character_sheet,
            self.path_sheet,
            self.background_sheet,
        )

    def register_warp_zone(
        self,
        x_pos: int,
        y_pos: int,
        location: "Map",
        final_x_pos: None,
        final_y_pos: None,
    ):
        """ Each position here is defined starting at 0, ending at #_of_pixels - 1."""

        if final_x_pos and final_y_pos:
            warp_zone = x_pos, y_pos, final_x_pos, final_y_pos, location
        else:
            warp_zone = x_pos, y_pos, x_pos, y_pos, location

        self._warp_zones.append(warp_zone)

    class InvalidObjectInSheetException(Exception):
        """ Raised when an invalid object type appears in
            the specified sheet."""

        pass
