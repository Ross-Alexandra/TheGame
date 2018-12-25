import logging
from multiprocessing.pool import ThreadPool

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
            self._main_loop()
        except Exception as e:
            logging.exception(f"Exception caught in main loop: {e}")

            self.running = False
            raise

        logging.info("Engine started.")

    def _main_loop(self):

        previous_pressed_keys = None
        logging.info("mail loop started.")

        while self.running:

            # Get the events, and the number of them.
            # Get the number here as it is used multiple
            # times, speeding this up.
            events = pygame.event.get()
            number_of_events = len(events)

            # Get the keys that were pressed.
            pressed_keys = [
                chr(index)
                for index, key_pressed in enumerate(pygame.key.get_pressed())
                if key_pressed
            ]

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
                keys_string = f"Pressed keys: {pressed_keys}"
                logging.info(keys_string)

                previous_pressed_keys = pressed_keys

    def _handle_event(self, event):

        logging.info("Got event of type {pygame.event.event_name(event)}")

        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()

        else:
            logging.debug("Unrecognized event type was unrecognized.")
