import logging
import sys

from thegame.engine import BaseMenu, Engine, Map
from thegame.engine.game_objects import (
    GameObject,
    InteractiveGameObject,
    PlayerCharacter,
)
from thegame.game_src import TheGame


def exit_button_interaction(game_context, *args, **kwargs):
    game_context.shutdown()


class ExitObject(InteractiveGameObject):
    """ An object used for testing that when interacted with
        will exit the game."""

    def interact(self, context):
        exit_button_interaction(context)


def start_game():
    logging.getLogger().setLevel(logging.INFO)

    if len(sys.argv) > 1 and sys.argv[1] == "-m":
        test_obj_one = GameObject({"Test1": "thegame/resources/TestBoxOne.png"})
        test_obj_two = GameObject({"Test2": "thegame/resources/TestBoxTwo.png"})
        exit_obj = ExitObject({"exit_sprite": "thegame/resources/ExitBox.png"})

        top_sheet = [
            [test_obj_one.clone() if not 8 <= _ <= 11 else None for _ in range(20)]
            for _ in range(20)
        ]
        character_sheet = [[None for _ in range(20)] for _ in range(20)]
        path_sheet = [[None for _ in range(20)] for _ in range(20)]
        bottom_sheet = [[test_obj_two.clone() for _ in range(20)] for _ in range(20)]

        character_sheet[10][10] = PlayerCharacter(
            sprite_locations={"PC_sprite": "thegame/resources/PC.png"}
        )

        top_sheet[6][10] = exit_obj

        main_map = Map(top_sheet, character_sheet, path_sheet, bottom_sheet)

        game = TheGame(
            initial_map=main_map,
            screen_width=300,
            screen_height=300,
            base_sprite_height=10,
            base_sprite_width=10,
            camera_width=30,
            camera_height=30,
            camera_x=10,
            camera_y=10,
        )

    else:
        game = TheGame(
            main_menu=BaseMenu(menu_image_location="thegame/resources/main_menu.png")
        )

        game.active_menu.register_interactive_zone(
            173, 228, 334, 303, exit_button_interaction
        )

    game_engine = Engine(game)
    game_engine.start()


if __name__ == "__main__":
    start_game()
