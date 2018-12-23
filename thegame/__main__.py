import pygame
from multiprocessing.pool import ThreadPool


class TheGame:
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
            print(f"Exception caught in main loop: {e}")

            self.running = False

    def _main_loop(self):
        while self.running:
            events = pygame.event.get()
            number_of_events = len(events)

            # Handle events if any have come in.
            if number_of_events > 0:

                # Each event should be independent of the other,
                # thus we should
                event_pool = ThreadPool(processes=number_of_events)

                for event in events:
                    event_pool.apply_async(self._handle_event, args=(event,))

    def _handle_event(self, event):
        if event.type == pygame.QUIT:
            print("Quit event called.")
            self.running = False
            pygame.quit()

if __name__ == "__main__":
    theGame = TheGame()
    theGame.start()
