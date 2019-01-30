import logging
import pprint
from multiprocessing.pool import ThreadPool

import pygame

from .base_game import BaseGame
from .base_menu import BaseMenu


class Engine:
    def __init__(self, game: BaseGame, event_thread_count: int = 10):
        """ Initialize the game engine and give it a game.

            Args:
                game(BaseGame): The game that this engine will start.
                event_thread_count(int): The number of threads to process events with.
                                         Default is 10 as 10 simultaneous events
                                         *should* be enough.
        """

        self.running = False

        self.display = None
        self.context = game
        self.width = game.screen_width
        self.height = game.screen_height
        self.size = self.width, self.height
        self.mouse_down_pos = None

        # Each event should be independent of the other,
        # thus we can process each one as if the others
        # didn't happen.
        self.event_pool = ThreadPool(processes=event_thread_count)

        pygame.init()

    def start(self):

        pygame.display.set_caption(self.context.name)
        self.display = pygame.display.set_mode(self.size)

        # Load in the game and load the active map if not a menu.
        self._load_map_sprites()
        self._load_menu_sprites()

        # Load the map if the game was not initialized with a
        # main menu.
        if self.context.active_menu is None:
            self.context.load_player_controlled_objects(self.context.active_screen)
            self.context.load_active_map()

        self.running = True
        try:
            logging.info("Starting engine.")
            self._main_loop()
            pygame.quit()

        except Exception as e:
            logging.exception(f"Exception caught in main loop: {e}")
            raise

        finally:
            logging.info("Pygame successfully uninitialized.")
            self.running = False

    def _main_loop(self):

        previous_pressed_keys = None
        logging.info("main loop started.")
        game_clock = pygame.time.Clock()
        game_sprites = pygame.sprite.Group()

        while self.running:

            # TODO: Attempt moving the keystroke logic into
            #       the event handling logic under both
            #       keypress and keyrelease events. This
            #       might deal with detecting holds
            #       auto-magically.

            # Get the keys that were pressed.
            pressed_keys = self._get_keystrokes()

            # Because this loop runs many times a second,
            # a "tap" is interpreted as a hold.
            # Do this to actually detect a tap.
            if pressed_keys == previous_pressed_keys:
                pressed_keys = []
            else:
                previous_pressed_keys = None

            # Handle the keys that were pressed
            if len(pressed_keys) > 0:
                self._handle_keystrokes(pressed_keys)
                previous_pressed_keys = pressed_keys

            # Get the events, and the number of them.
            # Get the number here as it is used multiple
            # times, speeding this up.
            events = pygame.event.get()

            # Handle events if any have come in.
            if len(events) > 0:

                self._schedule_events(events=events)

            # TODO: Find a more efficient method of this.
            #   clearing then re-adding all the sprites from
            #   the group seems inefficient.
            game_sprites.empty()

            # Discover which portion of the screen needs to be drawn
            if self.context.active_menu is not None:
                menu_sprite = self.context.active_menu.menu_image
                game_sprites.add(menu_sprite)
            else:
                onscreen_sprites = []
                fov_tile_sheet = self.context.camera.get_camera_fov(
                    self.context.active_screen
                )
                logging.debug(
                    f"Got the following fov_tile_sheet: {pprint.pformat(fov_tile_sheet, indent=4)}"
                )

                # Currently, this is done with (4 * camera_width * camera_height) loops.
                # the only way to reduce this is to not loop over rows full of Nones, but
                # this check isn't worth the gain.
                # Updates each sprites' x and y position.
                for layer in fov_tile_sheet[::-1]:
                    for row_index, row in enumerate(layer):
                        for cell_index, cell in enumerate(row):
                            if cell is not None:
                                logging.debug(
                                    f"{cell_index}: Setting the position of a {type(cell).__name__} on the screen."
                                )
                                cell.set_sprite_position(
                                    cell_index * self.context.base_sprite_width,
                                    row_index * self.context.base_sprite_height,
                                )
                                onscreen_sprites.append(cell.get_sprite())

                for sprite in onscreen_sprites:
                    game_sprites.add(sprite)

            game_sprites.draw(self.display)

            # TODO: In conjunction with the above todo, a more efficient way of drawing should be found.
            pygame.display.flip()

            # Run at 60fps
            game_clock.tick(60)

    def _load_map_sprites(self):

        game_object_list_set = set()

        # TODO: This is really ugly, and probably not optimal
        #       This should be re-looked at to be improved.
        for game_map in self.context.maps.values():
            for layer in game_map.tile_sheets:
                for row in layer:
                    for game_object in row:
                        if game_object is not None:
                            game_object_list_set.add(game_object.sprite_location)

        for game_object_location in game_object_list_set:
            image = pygame.image.load(game_object_location).convert_alpha()

            self.context.object_images[game_object_location] = image

    def _load_menu_sprites(self):
        for menu in self.context.menus.values():
            sprite = pygame.sprite.Sprite()
            sprite.image = pygame.image.load(menu.menu_image_location).convert_alpha()
            sprite.rect = sprite.image.get_rect()
            menu.menu_image = sprite

    def _schedule_events(self, events):

        # Because the events are running in a separate thread, an
        # exception thrown by them is hidden in the ThreadPool.
        # In order to tell if an exception occurred in any of the event
        # handlers, we store a future to each call in exception_check,
        # and once all of the events have been scheduled, we get a value
        # from these futures. If an exception was thrown, this get call
        # will also throw it.
        # TODO: Find a better way to do this, currently we only have
        #       a concurrency gain from doing these in separate threads,
        #       this method still wont return until the longest of the
        #       threads has finished though. An ideal solution would allow
        #       for exception checking, but return from this method *before*
        #       the event handler has finished running.
        exception_check = []
        for event in events:
            if self.running:
                exception_check.append(
                    (
                        self.event_pool.apply_async(self._handle_event, args=(event,)),
                        event,
                    )
                )

        for possible_exception, event in exception_check:
            try:
                possible_exception.get()
            except Exception as e:
                self.running = False
                logging.exception(
                    f"Caught exception while handling "
                    f"'{pygame.event.event_name(event.type)}' event: '{e}'."
                )
                break

    def _handle_event(self, event):
        logging.debug(f"Got event of type {pygame.event.event_name(event.type)}")

        # If the game is not running, don't handle events.
        if event.type == pygame.QUIT or not self.running:
            self.running = False

        if event.type == pygame.MOUSEBUTTONUP and self.mouse_down_pos is not None:

            # Get the initial and final position positions of the mouse from when the click (and hold)
            # occurred.
            init_x, init_y = self.mouse_down_pos
            final_x, final_y = pygame.mouse.get_pos()
            self.mouse_down_pos = None

            logging.info(f"Mouse button released at position ({final_x}, {final_y})")

            # If the current active screen is a menu, then attempt to call an
            # interactive zone (only works if one has been registered where the click happened.)
            if isinstance(self.context.active_screen, BaseMenu):
                self.context.active_menu.call_interactive_zone_by_click(
                    init_x, init_y, final_x, final_y, game_context=self.context
                )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down_pos = pygame.mouse.get_pos()
            press_x, press_y = self.mouse_down_pos

            logging.info(f"Mouse button pressed at position ({press_x}, {press_y})")

        else:
            logging.debug(
                f"Unrecognized event type '{pygame.event.event_name(event.type)}' found."
            )

    def _handle_keystrokes(self, keystrokes):

        up_arrow = chr(273)
        down_arrow = chr(274)

        for player_controlled_object in self.context.player_controlled_objects.keys():
            # TODO: Examine doing this in threads.
            player_controlled_object.player_interaction(
                keystrokes=keystrokes, context=self.context
            )

        # If the current active screen is a menu
        if isinstance(self.context.active_screen, BaseMenu):

            # If there is currently no focused interactive zone.
            if self.context.active_menu.focused_zone is None:

                # If the UP arrow is pressed, set the focused zone to the last one.
                if up_arrow in keystrokes:
                    self.context.active_menu.focused_zone = (
                        self.context.active_menu.interactive_zone_count() - 1
                    )

                # If the DOWN arrow is pressed, set the focused zone to the first one.
                elif down_arrow in keystrokes:
                    self.context.active_menu.focused_zone = 0

            # If there is currently a focused interactive zone.
            else:

                # If the UP arrow is pressed, set the focused zone to the previous one.
                if up_arrow in keystrokes:
                    self.context.active_menu.focused_zone -= 1
                    if self.context.active_menu.focused_zone < 0:
                        self.context.active_menu.focused_zone = (
                            self.context.active_menu.interactive_zone_count() - 1
                        )

                # If the DOWN arrow is pressed, set the focused zone to the next one.
                elif down_arrow in keystrokes:
                    self.context.active_menu.focused_zone += 1
                    if (
                        self.context.active_menu.focused_zone
                        >= self.context.active_menu.interactive_zone_count()
                    ):
                        self.context.active_menu.focused_zone = 0

                # If the ENTER key is pressed, call the interaction associated with
                # the currently focused interactive zone.
                elif "\r" in keystrokes or "\n" in keystrokes:
                    self.context.active_menu.call_interactive_zone_by_index(
                        self.context.active_menu.focused_zone, self.context
                    )

        keys_string = f"Pressed keys: {keystrokes}"
        logging.info(keys_string)

    @staticmethod
    def _get_keystrokes():
        """TODO: As of current, pressing two keys at the same time
            (well, almost the same time, like a normal human would)
            causes a keystroke of the first letter, then both letters
            to occur. This should be changed somehow to just have the
            one keystroke of both characters.
            This may be solved by movement ticks, as there is an extremely
            short period of time where there is only one key down when
            there should be two."""

        pressed_keys = [
            chr(index)
            for index, key_pressed in enumerate(pygame.key.get_pressed())
            if key_pressed
        ]

        return pressed_keys
