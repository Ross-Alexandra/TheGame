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
