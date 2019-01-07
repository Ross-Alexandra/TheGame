import logging

from thegame.engine import Engine
from thegame.engine.base_menu import BaseMenu
from thegame.game_src import TheGame


def start_game():
    logging.getLogger().setLevel(logging.INFO)

    game = TheGame(main_menu=BaseMenu("main_menu.png"))
    game_engine = Engine(game)
    game_engine.start()


if __name__ == "__main__":
    start_game()
