import logging
from abc import abstractmethod

from . import GameObject


class PlayerControlledObject(GameObject):
    def __init__(self, sprite_location: str, animation: str = None, name: str = None):
        super().__init__(sprite_location, animation, name)

    @abstractmethod
    def player_interaction(self, keystrokes, context):
        """ Whenever a key is pressed, this method is called
            by the engine with the keystroke. This method should
            implement controls for possible interactions. For example
            for a player to move, a test of "w" in keystroke to
            tell if w was pressed, and if it is, run a method
            to move the character forward."""
        raise NotImplementedError()


class PlayerCharacter(PlayerControlledObject):
    """ An ease-of-use class that embodies a PC.
        This class is a PlayerControlledObject which
        has built in functionality for movement."""

    def player_interaction(self, keystrokes, context):

        # Check if any of WASD were pressed, and if so move.
        if (
            "w" in keystrokes
            or "s" in keystrokes
            or "a" in keystrokes
            or "d" in keystrokes
        ):
            self.move(
                context,
                up="w" in keystrokes,
                down="s" in keystrokes,
                left="a" in keystrokes,
                right="d" in keystrokes,
            )

    def move(self, context, up=False, down=False, left=False, right=False):
        """ A class that moves the PC around the map in the directions specified.
            Only one direction is supported at a time.
            Note, going up always takes priority, going up or down takes priority
            over going left and right, and going left takes priority over going right.
            This means that if up and down, then the PC will move up; if up and
            left, then the PC will move up; if down and right, then the PC will
            move down; and if left and right, the PC will move left."""

        current_pos = context.player_controlled_objects[self]
        sheet = context.active_screen.CHARACTER_SHEET_INDEX
        logging.info(
            f"PlayerControlledObject at {current_pos} is moving with {(up, down, left, right)}. "
            f"Current value at location is: "
            f"{context.active_screen.tile_sheets[sheet][current_pos[0]][current_pos[1]]}"
        )

        if up:
            new_pos = (current_pos[0], current_pos[1] - 1)

        elif down:
            new_pos = (current_pos[0], current_pos[1] + 1)

        elif left:
            new_pos = (current_pos[0] - 1, current_pos[1])

        elif right:
            new_pos = (current_pos[0] + 1, current_pos[1])
        else:
            logging.warning("CharacterObject.move called with all parameters False.")
            return

        context.player_controlled_objects[self] = new_pos
        context.active_screen.swap(current_pos, new_pos, sheet)
