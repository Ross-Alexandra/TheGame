import logging
from multiprocessing.pool import ThreadPool
from time import sleep

import pygame


class Engine:
    def __init__(self):
        self.width = 240
        self.height = 180
        self.size = self.width, self.height
        self.running = False

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

            # Get the events, and the number of them.
            # Get the number here as it is used multiple
            # times, speeding this up.
            events = pygame.event.get()
            number_of_events = len(events)

            # Get the keys that were pressed.
            pressed_keys = self._get_keystrokes()

            # Because this loop runs many times a second,
            # a "tap" is interpreted as a hold.
            # Do this to actually detect a tap.
            if pressed_keys == previous_pressed_keys:
                pressed_keys = []
            else:
                previous_pressed_keys = None

            # Handle events if any have come in.
            if number_of_events > 0:

                # Each event should be independent of the other,
                # thus we can process each one as if the others
                # didn't happen.
                event_pool = ThreadPool(processes=number_of_events)

                for event in events:
                    event_pool.apply_async(self._handle_event, args=(event,))

            # Handle the keys that were pressed
            if len(pressed_keys) > 0:
                self._handle_keystrokes(pressed_keys)
                previous_pressed_keys = pressed_keys

    def _handle_event(self, event):

        logging.debug(f"Got event of type {pygame.event.event_name(event.type)}")

        if event.type == pygame.QUIT:
            self.running = False

        else:
            logging.debug("Unrecognized event type found.")

    def _handle_keystrokes(self, keystrokes):
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
