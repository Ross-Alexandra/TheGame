class GameObject:
    """ An object that will be used to fill the objects sheet of a game."""

    def __init__(self, sprite, animation: None):

        self.sprite = sprite
        if animation:
            self.animation = animation
