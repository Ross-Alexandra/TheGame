import random


class GameObject:
    def __init__(
        self,
        sprite_locations: dict,
        initial_sprite: str = None,
        animation: str = None,
        name: str = None,
    ):
        """ An object that will be used to fill the objects sheet of a game.

            Args:
                sprite_locations(dict): A dictionary of sprites for the game object given
                                        as {name:location}.
                initial_sprite(str)   : The sprite that should be initally displayed. It should
                                        exist in sprite_locations.
                animation(str)        : A path to an animated image. NOT IMPLEMENTED
                name(str)             : The name of the GameObject.
        """

        self.sprite_locations = sprite_locations
        self._loaded_sprites = {}  # {location,Sprite}
        self.animation = animation
        self.name = name
        if initial_sprite is None and sprite_locations:
            # If no initial sprite is given, choose a random sprite as the active sprite.
            self.active_sprite = list(sprite_locations)[
                random.randint(0, len(sprite_locations) - 1)
            ]
        elif initial_sprite is not None and initial_sprite not in sprite_locations:
            raise AttributeError(
                f"{initial_sprite} not found in {type(self).__name__}'s initial dictionary."
            )
        else:
            self.active_sprite = initial_sprite

    def clone(self):
        clone = GameObject(
            sprite_locations=self.sprite_locations,
            animation=self.animation,
            initial_sprite=self.active_sprite,
            name=self.name,
        )

        return clone

    def register_loaded_sprite(self, location, loaded_sprite):
        self._loaded_sprites[location] = loaded_sprite

    def deregister_loaded_sprites(self):
        self.active_sprite = None
        self._loaded_sprites = {}

    def set_sprite_position(self, pos_x, pos_y):
        if not self._loaded_sprites:
            raise AttributeError(
                f"Tried to set {type(self).__name__}'s position without registering a loaded sprite."
            )
        loaded_sprite = self._loaded_sprites[self.sprite_locations[self.active_sprite]]

        loaded_sprite.rect = loaded_sprite.image.get_rect()
        loaded_sprite.rect.x = pos_x
        loaded_sprite.rect.y = pos_y

    def add_sprite_location(self, name, location):
        self.sprite_locations[name] = location

    def get_sprite(self):
        # if self._loaded_sprites is empty
        if not self._loaded_sprites:
            raise AttributeError(
                f"Tried to get {type(self).__name__}'s sprite without registering any sprites."
            )
        # if self.active_sprite is None but _loaded_sprites is not empty
        if self.active_sprite is None:
            raise AttributeError(
                f"{type(self).__name__}'s contains loaded sprites but has no active sprite"
            )
        return self._loaded_sprites[self.sprite_locations[self.active_sprite]]

    def set_sprite(self, sprite_name):
        if sprite_name not in self.sprite_locations:
            raise AttributeError(
                f"Sprite {sprite_name} not found in {type(self).__name__}"
            )
        self.active_sprite = sprite_name

    def get_active_sprite_location(self):
        return self.sprite_locations[self.active_sprite]

    def get_sprite_locations(self):
        return list(self.sprite_locations.values())

    def __str__(self):
        if self.name:
            return type(self).__name__ + f": {self.name}"
        else:
            return type(self).__name__
