import logging
from multiprocessing.pool import ThreadPool

import pygame

from .base_game import BaseGame
from .base_menu import BaseMenu


class Engine:
    def __init__(self, game: BaseGame):
        self.width = 240
        self.height = 180
        self.size = self.width, self.height
        self.running = False
        self.mouse_down_pos = None
        self.context = game

        pygame.init()
        pygame.display.set_caption("TheGame")
        pygame.display.set_mode(self.size)

    def start(self):
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

        while self.running:
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
            number_of_events = len(events)

            # Handle events if any have come in.
            if number_of_events > 0:

                # Each event should be independent of the other,
                # thus we can process each one as if the others
                # didn't happen.
                event_pool = ThreadPool(processes=number_of_events)

                exception_check = []
                for event in events:
                    if self.running:
                        exception_check.append(
                            (
                                event_pool.apply_async(
                                    self._handle_event, args=(event,)
                                ),
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

            # If the current active screen is a menu, then call attempt to call and
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
                            self.context.active_menu.interactive_zone_count()
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
