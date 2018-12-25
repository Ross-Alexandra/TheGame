import logging

from thegame.engine.engine import Engine


def start_game():
    logging.getLogger().setLevel(logging.INFO)

    game_engine = Engine()
    game_engine.start()


if __name__ == "__main__":
    start_game()
