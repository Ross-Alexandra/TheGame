class GameObject:
    """ An object that will be used to fill the objects sheet of a game."""

    def __init__(
        self,
        sprite_locations: dict,
        initial_sprite: str = None,
        animation: str = None,
        name: str = None,
    ):
        """ 
            sprite_locations {name,location}
            _loaded_sprites {location, Sprite}
        """
        self.sprite_locations = sprite_locations
        self._loaded_sprites = {}
        self.animation = animation
        self.name = name
        if initial_sprite is None and bool(sprite_locations):
            self.active_sprite = list(self.sprite_locations.keys())[0]
        else:
            self.active_sprite = initial_sprite

    def clone(self):
        clone = GameObject(
            sprite_locations=self.sprite_locations,
            animation=self.animation,
            initial_sprite=self.active_sprite,
        )

        return clone

    def register_loaded_sprite(self, loaded_sprite, location):
        self._loaded_sprites[location] = loaded_sprite

    def deregister_loaded_sprites(self):
        self.active_sprite = None
        self._loaded_sprites = {}

    def set_sprite_position(self, pos_x, pos_y):
        if self._loaded_sprites == {}:
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
        if not bool(self._loaded_sprites):
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
