from thegame.engine.game_objects import GameObject, PlayerControlledObject


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

        self.foreground_sheet = foreground_sheet
        self.path_sheet = path_sheet
        self.background_sheet = background_sheet
        self.character_sheet = character_sheet

        if validate:
            self._validate()

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

    @property
    def player_controlled_objects(self):

        player_controlled_objects = []

        for sheet in self.tile_sheets:
            for row_index, row in enumerate(sheet):
                for cell_index, cell in enumerate(row):
                    if isinstance(cell, PlayerControlledObject):
                        player_controlled_objects.append((cell, cell_index, row_index))

        return player_controlled_objects

    def swap(self, tile_one: tuple, tile_two: tuple, sheet: int):
        """ Swap two tiles.

            Args:
                tile_one(tuple): x,y of one of the tiles
                tile_two(tuple): x,y of the other tile.
                sheet(int): The sheet number that the swap is happening on.
        """

        if not 0 <= sheet <= 3:
            raise ValueError(
                f"Attempted to swap tiles on sheet level {sheet}, which is not a valid sheet. Please"
                " swap on sheet [0-3]."
            )

        tile_one_x = tile_one[0]
        tile_one_y = tile_one[1]
        tile_two_x = tile_two[0]
        tile_two_y = tile_two[1]

        _ = self.tile_sheets[sheet][tile_one_x][tile_two_y]
        self.tile_sheets[sheet][tile_one_x][tile_one_y] = self.tile_sheets[sheet][
            tile_two_x
        ][tile_two_y]
        self.tile_sheets[sheet][tile_two_x][tile_two_y] = _

    def _validate(self):
        """ Validate that each sheet is valid, if its not, raise an appropriate exception. """

        try:
            # Check that all the objects in the foreground sheet are GameObjects or None.
            if not all(
                isinstance(o, GameObject) or o is None
                for row in self.foreground_sheet
                for o in row
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject or None found in object sheet."
                )

            # Check that all the objects in the path sheet are GameObjects or None.
            elif not all(
                isinstance(o, GameObject) or o is None
                for row in self.path_sheet
                for o in row
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject or None found in path sheet."
                )

            # Check that all tha objects in the background sheet are GameObjects or None.
            elif not all(
                isinstance(o, GameObject) or o is None
                for row in self.background_sheet
                for o in row
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject or None found in background sheet."
                    f" Either correct this issue, or turn validation off."
                )

            # Check that all the objects in the character sheet are GameObjects or None.
            elif not all(
                isinstance(o, GameObject) or o is None
                for row in self.character_sheet
                for o in row
            ):
                raise self.InvalidObjectInSheetException(
                    f"Object not of type GameObject or None found in character sheet."
                    f" Either correct this issue, or turn validation off."
                )
        except TypeError:
            raise ValueError("All sheets must be 2D, ie an iterable of an iterable.")

        return True

    def register_warp_zone(
        self,
        x_pos: int,
        y_pos: int,
        location: "Map",
        warp_x_location: int,
        warp_y_location: int,
        final_x_pos: int = None,
        final_y_pos: int = None,
    ):
        """ Each position here is defined starting at 0, ending at #_of_pixels - 1.

            Args:
                x_pos: The first x position where the warp zone exists.
                y_pos: The first y position where the warp zone exists.
                location: The map that we're warping to.
                warp_x_location: The x position of where we're warping to.
                warp_y_location: The y position of where we're warping to.
                final_x_pos: The x position of the other corner of the square of the warp zone.
                final_y_pos: The y position of the other corner of the square of teh warp zone."""

        # Check to see if the warp location exists in the location.
        try:
            location.tile_sheets[self.CHARACTER_SHEET_INDEX][warp_x_location][
                warp_y_location
            ]
        except IndexError:
            raise self.InvalidWarpZoneLocationException

        if final_x_pos is not None and final_y_pos is not None:

            # Swap the final and the initial if the final is less that the initial.
            if final_y_pos < y_pos:
                _ = final_y_pos
                final_y_pos = y_pos
                y_pos = _
            if final_x_pos < x_pos:
                _ = final_x_pos
                final_x_pos = x_pos
                x_pos = _

            warp_zone = (
                x_pos,
                y_pos,
                final_x_pos,
                final_y_pos,
                location,
                warp_x_location,
                warp_y_location,
            )
        else:
            warp_zone = (
                x_pos,
                y_pos,
                x_pos,
                y_pos,
                location,
                warp_x_location,
                warp_y_location,
            )

        self._warp_zones.append(warp_zone)

    class InvalidObjectInSheetException(Exception):
        """ Raised when an invalid object type appears in
            the specified sheet."""

        pass

    class InvalidWarpZoneLocationException(Exception):
        """ Raised when a warp zone is created to a location outside of
            a map's bounds. """

        pass
