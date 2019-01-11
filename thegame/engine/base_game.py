from .base_menu import BaseMenu
from .map import Map


class BaseGame:
    """ This class represents an abstract game class
        that all classes that the game engine use should
        implement."""

    def __init__(
        self,
        main_menu: BaseMenu = None,
        initial_map: Map = None,
        initial_map_name="Initial Map",
    ):

        if main_menu is None and initial_map is None:
            raise SyntaxError(
                "One of main_menu or initial_map must be specified to initialize a game."
            )

        # Setup the active map and menu. Each of th
        self.active_menu = main_menu

        # Set the current active screen to be drawn.
        self.active_screen = main_menu if main_menu is not None else initial_map

        # Create a dictionary of the maps that will be used in the game
        if initial_map:
            self.maps = {initial_map_name: initial_map}
        else:
            self.maps = {}

    def register_map(self, map_name: str, new_map: Map):
        self.maps[map_name] = new_map

    def change_map(self, map_name):
        new_map = self.maps.get(map_name, None)

        if new_map is None:
            raise ValueError(f"No map registered with name '{map_name}'")

        # Set the active screen to the new map. This will close any menus.
        self.active_screen = new_map
