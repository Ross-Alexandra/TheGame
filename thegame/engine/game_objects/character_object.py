import logging
from abc import abstractmethod

from . import GameObject, InteractiveGameObject


class PlayerControlledObject(GameObject):
    def __init__(
        self,
        sprite_locations: dict,
        initial_sprite: str = None,
        animation: str = None,
        name: str = None,
    ):
        super().__init__(sprite_locations, animation, name)

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

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __init__(
        self,
        sprite_locations: dict,
        initial_sprite: str = None,
        animation: str = None,
        name: str = None,
        facing_direction: int = NORTH,
    ):
        super().__init__(
            sprite_locations=sprite_locations,
            initial_sprite=initial_sprite,
            animation=animation,
            name=name,
        )
        self.facing = facing_direction
        if initial_sprite is not None:
            self.set_sprite(initial_sprite)

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

        if "\r" in keystrokes or "\n" in keystrokes:
            self.call_interaction(context)

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
        logging.debug(
            f"PlayerControlledObject at {current_pos} is moving with {(up, down, left, right)}. "
        )

        if up:
            new_pos = (current_pos[0], current_pos[1] - 1)
            self.set_sprite("PC_north")

        elif down:
            new_pos = (current_pos[0], current_pos[1] + 1)
            self.set_sprite("PC_south")

        elif left:
            new_pos = (current_pos[0] - 1, current_pos[1])
            self.set_sprite("PC_west")

        elif right:
            new_pos = (current_pos[0] + 1, current_pos[1])
            self.set_sprite("PC_east")
        else:
            logging.warning("CharacterObject.move called with all parameters False.")
            return

        context.player_controlled_objects[self] = new_pos
        context.active_screen.swap(current_pos, new_pos, sheet)

    def call_interaction(self, context):

        pc_location = context.player_controlled_objects[self]

        if self.facing is PlayerCharacter.NORTH:
            facing_location = (pc_location[0], pc_location[1] - 1)
        elif self.facing is PlayerCharacter.EAST:
            facing_location = (pc_location[0] + 1, pc_location[1])
        elif self.facing is PlayerCharacter.SOUTH:
            facing_location = (pc_location[0], pc_location[1] + 1)
        elif self.facing is PlayerCharacter.WEST:
            facing_location = (pc_location[0] - 1, pc_location[1])
        else:
            raise AttributeError(
                "Player Character is currently set to a value other than 0-3 "
                "(North, East, South, West)."
            )
        logging.info(
            f"PlayerCharacter attempting to interact with InteractiveGameObject at location: {facing_location}"
        )

        sheets = {
            context.active_screen.FOREGROUND_SHEET_INDEX,
            context.active_screen.CHARACTER_SHEET_INDEX,
            context.active_screen.PATH_SHEET_INDEX,
            context.active_screen.BACKGROUND_SHEET_INDEX,
        }
        facing_x = facing_location[0]
        facing_y = facing_location[1]

        # Check all 4 sheets from top to bottom looking for an
        # interactive game object.
        igo = None
        for sheet in sheets:
            if isinstance(
                context.active_screen.tile_sheets[sheet][facing_y][facing_x],
                InteractiveGameObject,
            ):
                igo = context.active_screen.tile_sheets[sheet][facing_y][facing_x]
                break

        if igo is not None:
            igo.interact(context)
