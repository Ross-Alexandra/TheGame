class GameObject:
    """ An object that will be used to fill the objects sheet of a game."""

    def __init__(self, sprite_location: str, animation: str = None, name: str = None):

        self.sprite_location = sprite_location
        self.animation = animation
        self._loaded_sprite = None
        self.name = name

    def clone(self):
        clone = GameObject(
            sprite_location=self.sprite_location, animation=self.animation
        )

        return clone

    def register_loaded_sprite(self, loaded_sprite):
        self._loaded_sprite = loaded_sprite

    def set_sprite_position(self, pos_x, pos_y):
        if self._loaded_sprite is None:
            raise ValueError(
                f"Tried to set {type(self).__name__}'s position without registering a loaded sprite."
            )

        self._loaded_sprite.rect = self._loaded_sprite.image.get_rect()
        self._loaded_sprite.rect.x = pos_x
        self._loaded_sprite.rect.y = pos_y

    def get_sprite(self):
        if self._loaded_sprite is None:
            raise ValueError(
                f"Tried to get {type(self).__name__}'s sprite without registering it."
            )

        return self._loaded_sprite

    def deregister_loaded_sprite(self):
        self._loaded_sprite = None

    def __str__(self):
        if self.name:
            return type(self).__name__ + f": {self.name}"
        else:
            return type(self).__name__
