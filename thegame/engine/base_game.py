import logging

import pygame

from .base_menu import BaseMenu
from .camera import Camera
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
        screen_width: int = 600,
        screen_height: int = 600,
        base_sprite_width: int = 30,
        base_sprite_height: int = 30,
        camera_width: int = 10,
        camera_height: int = 10,
        camera_x: int = 10,
        camera_y: int = 10,
    ):

        if main_menu is None and initial_map is None:
            raise SyntaxError(
                "One of main_menu or initial_map must be specified to initialize a game."
            )

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.base_sprite_width = base_sprite_width
        self.base_sprite_height = base_sprite_height

        # The camera is a screen_width x screen_height
        # rectangle representing what of the map can be
        # seen at any given time.
        # This camera will move around either with the
        # character, or as directed by a cutscene.
        # The number of sprites left and right on the
        # screen is:
        #   screen_width / base_sprite_width
        # The number of sprites up and down on the
        # screen is:
        #   screen_height / base_sprite_height.
        self.camera = Camera(
            camera_width=camera_width,
            camera_height=camera_height,
            camera_x=camera_x,
            camera_y=camera_y,
        )

        # Setup the active map and menu. Each of th
        self.active_menu = main_menu

        # Set the current active screen to be drawn.
        self.active_screen = main_menu if main_menu is not None else initial_map

        # Create a dictionary of the maps that will be used in the game
        if initial_map:
            self.maps = {initial_map_name: initial_map}
            self.menus = {}
        else:
            self.menus = {"main menu": main_menu}
            self.maps = {}

        self.object_images = {}

    def load_active_map(self):
        for sheet in self.active_screen.tile_sheets:
            for row_index, row in enumerate(sheet):
                for cell_index, cell in enumerate(row):
                    if cell is not None:
                        sprite = pygame.sprite.Sprite()
                        sprite.image = self.object_images[cell.sprite_location]

                        cell.register_loaded_sprite(sprite)

    def unload_active_map(self):
        for sheet in self.active_screen.tile_sheets:
            for row_index, row in enumerate(sheet):
                for cell_index, cell in enumerate(row):
                    if cell is not None:
                        sprite = pygame.sprite.Sprite()
                        sprite.image = self.object_images[cell]

                        cell.deregister_loaded_sprite()

    def register_map(self, map_name: str, new_map: Map):
        self.maps[map_name] = new_map

    def change_map(self, map_name):
        new_map = self.maps.get(map_name, None)

        if new_map is None:
            raise ValueError(f"No map registered with name '{map_name}'")

        self.unload_active_map()
        # Set the active screen to the new map. This will close any menus.
        self.active_screen = new_map
        self.active_menu = None
        self.load_active_map()

    def open_meu(self, menu_name):
        new_menu = self.menus.get(menu_name, None)

        if new_menu is None:
            raise ValueError(f"No menu registered with name '{menu_name}'")

        if self.active_menu is None:
            self.unload_active_map()

        self.active_menu = self.active_screen = new_menu

    @staticmethod
    def shutdown():
        pygame.event.post(pygame.event.Event(pygame.QUIT, dict=None))
        logging.info("Quit event posted to event queue. Game shutting down.")
