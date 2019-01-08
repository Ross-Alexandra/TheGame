from abc import abstractmethod

from thegame.engine import BaseGame

from .game_object import GameObject


class InteractiveGameObject(GameObject):
    """ A game object which can be interacted with
        by the user."""

    @abstractmethod
    def interact(self, game: BaseGame):
        """ The method that will be called when this object is interacted with."""

        pass
