import logging

from thegame.engine.engine import Engine


def start_game():
    logging.getLogger().setLevel(logging.INFO)

    if __name__ == "__main__":
        game_engine = Engine()
        game_engine.start()


start_game()
