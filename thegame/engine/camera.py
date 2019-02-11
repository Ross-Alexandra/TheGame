""" A camera class used by base_game to handle showing only portions of each
    map at a time."""
import logging
import pprint

from .map import Map


class Camera:
    """ A Camera class for dealing with the game camera."""

    def __init__(self, camera_width, camera_height, camera_x, camera_y):
        """ In order to have a center of the screen, camera_width and camera_height
            act as if they are the next highest odd number (presuming they're even.)
            If its odd, the value doesn't change."""
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_x = camera_x
        self.camera_y = camera_y

    def get_camera_fov(self, game_map: Map):
        #  x x x x x
        #      ^
        # camera_x = 2
        # camera_width = 3
        # 1 - (3 // 2) = 2 - 1 = 1
        # 1 + (3 // 2) = 2 + 1 = 3
        #
        leftmost_sprite = self.camera_x - (self.camera_width // 2)
        rightmost_sprite = self.camera_x + (self.camera_width // 2)

        topmost_sprite = self.camera_y - (self.camera_height // 2)
        bottommost_sprite = self.camera_y + (self.camera_height // 2)

        # TODO: There may be a better way to do this.
        # Current functionality:
        #   Take each layer, and break it into rows. Assemble a list of those rows in the
        #   range from topmost to bottom most, and slice those rows to only include between
        #   leftmost and rightmost.
        #   Further, if the fov of the camera would put a portion of the camera outside
        #   of the map's bounds (think a negative leftmost_sprite) then we return Nones
        #   for any outside position.
        fov_tile_sheet = []
        for tile_sheet in game_map.tile_sheets:

            shrunk_tile_sheet = []
            add_top_rows = []
            add_bottom_rows = []

            if topmost_sprite < 0:
                _topmost_sprite = 0
                add_top_rows = [
                    [None for _ in range(self.camera_width)]
                    for _ in range(abs(topmost_sprite))
                ]
            else:
                _topmost_sprite = topmost_sprite

            if bottommost_sprite >= len(tile_sheet):
                _bottommost_sprite = len(tile_sheet) - 1
                add_bottom_rows = [
                    [None for _ in range(self.camera_width)]
                    for _ in range(bottommost_sprite - len(tile_sheet) + 1)
                ]
            else:
                _bottommost_sprite = bottommost_sprite

            if add_top_rows:
                shrunk_tile_sheet += add_top_rows

            for row in tile_sheet[_topmost_sprite : _bottommost_sprite + 1]:

                fov_row = []

                if leftmost_sprite < 0:
                    _leftmost_sprite = 0
                    fov_row += [None for _ in range(abs(leftmost_sprite))]
                else:
                    _leftmost_sprite = leftmost_sprite

                if rightmost_sprite >= len(row):
                    _rightmost_sprite = len(tile_sheet) - 1
                    fov_row += row[_leftmost_sprite : _rightmost_sprite + 1]
                    fov_row += [None for _ in range(rightmost_sprite - len(row) + 1)]
                else:
                    _rightmost_sprite = rightmost_sprite
                    fov_row += row[_leftmost_sprite : _rightmost_sprite + 1]

                shrunk_tile_sheet.append(fov_row)

            if add_bottom_rows:
                shrunk_tile_sheet += add_bottom_rows

            fov_tile_sheet.append(shrunk_tile_sheet)

        return fov_tile_sheet
