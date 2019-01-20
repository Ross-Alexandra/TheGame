import logging


class BaseMenu:
    """ A base class for defining the behavior of a menu in a game.

        This menu is made up of "interactive zones." These zones
        are areas that when clicked on, hovered over, etc, will
        have custom functions called with the event."""

    INIT_X_POS_INDEX = 0
    INIT_Y_POS_INDEX = 1
    FINAL_X_POS_INDEX = 2
    FINAL_Y_POS_INDEX = 3
    INTERACTION_INDEX = 4

    def __init__(self, menu_image):
        self.menu_image = menu_image
        self.focused_zone = None
        self._interactive_zones = []

    def register_interactive_zone(
        self, init_x_pos, init_y_pos, final_x_pos, final_y_pos, interaction
    ):
        """ Each position here is defined starting at 0, ending at #_of_pixels - 1.

            When a user interacts with arrow keys, the focused zone attribute will be set
            based on the order of the interactive zones. When a user presses the UP key,
            the last zone registered will be focused, when a user presses the DOWN key
            the first zone will be registered. If a zone is already in focus, pressing UP
            will cause the previous zone to be focused, and the DOWN key will cause the
            next zone to be focused. When the ENTER key is pressed, the currently focused
            zone's interaction to be called."""

        # If any of the finals are smaller that their inits, flip them
        if final_x_pos < init_x_pos:
            _ = init_x_pos
            init_x_pos = final_x_pos
            final_x_pos = _

        if final_y_pos < init_y_pos:
            _ = init_y_pos
            init_y_pos = final_y_pos
            final_y_pos = _

        new_interactive_zone = (
            init_x_pos,
            init_y_pos,
            final_x_pos,
            final_y_pos,
            interaction,
        )

        for interactive_zone in self._interactive_zones:

            # Check if this interactive_zone overlaps with a pre-existing one.
            if (
                (
                    interactive_zone[self.INIT_X_POS_INDEX]
                    <= init_x_pos
                    <= interactive_zone[self.FINAL_X_POS_INDEX]
                    or interactive_zone[self.INIT_X_POS_INDEX]
                    <= final_x_pos
                    <= interactive_zone[self.FINAL_X_POS_INDEX]
                )
                and (
                    interactive_zone[self.INIT_Y_POS_INDEX]
                    <= init_y_pos
                    <= interactive_zone[self.FINAL_Y_POS_INDEX]
                    or interactive_zone[self.INIT_Y_POS_INDEX]
                    <= final_y_pos
                    <= interactive_zone[self.FINAL_Y_POS_INDEX]
                )
                or (
                    interactive_zone[self.INIT_X_POS_INDEX] >= init_x_pos
                    and interactive_zone[self.FINAL_X_POS_INDEX] <= final_x_pos
                    and interactive_zone[self.INIT_Y_POS_INDEX] >= init_y_pos
                    and interactive_zone[self.FINAL_Y_POS_INDEX] <= final_y_pos
                )
            ):
                exception_string = (
                    f"Interactive zone being registered with ({init_x_pos}, {init_y_pos}),"
                    f"({final_x_pos}, {final_y_pos}) overlaps with pre-existing zone."
                    f"({interactive_zone[self.INIT_X_POS_INDEX]}, {interactive_zone[self.INIT_Y_POS_INDEX]}), "
                    f"({interactive_zone[self.FINAL_X_POS_INDEX]}, {interactive_zone[self.FINAL_X_POS_INDEX]})."
                )

                raise self.OverlappingInteractiveZoneException(exception_string)

        logging.debug(f"Creating interactive zone: {new_interactive_zone} ")
        self._interactive_zones.append(new_interactive_zone)

    def get_interactive_zones(self):
        """ Return a copy list of interactive zones. """
        return list(self._interactive_zones)

    def call_interactive_zone_by_index(self, index, game_context):
        self._interactive_zones[index][self.INTERACTION_INDEX](
            game_context=game_context
        )

    def call_interactive_zone_by_click(
        self, init_x_pos, init_y_pos, final_x_pos, final_y_pos, game_context
    ):
        """ Call any interactions should the ranges passed fall within the interactive_zone."""

        # Ensure that *for comparison only* the finals are larger that the initials.
        comparison_init_x = init_x_pos if init_x_pos < final_x_pos else final_x_pos
        comparison_final_x = final_x_pos if init_x_pos < final_x_pos else init_x_pos

        comparison_init_y = init_y_pos if init_y_pos < final_y_pos else final_y_pos
        comparison_final_y = final_y_pos if init_y_pos < final_y_pos else init_y_pos

        for interactive_zone in self._interactive_zones:

            # Check if this interactive_zone was clicked.
            if (
                interactive_zone[self.INIT_X_POS_INDEX]
                <= comparison_init_x
                <= interactive_zone[self.FINAL_X_POS_INDEX]
                and interactive_zone[self.INIT_X_POS_INDEX]
                <= comparison_final_x
                <= interactive_zone[self.FINAL_X_POS_INDEX]
            ) and (
                interactive_zone[self.INIT_Y_POS_INDEX]
                <= comparison_init_y
                <= interactive_zone[self.FINAL_Y_POS_INDEX]
                and interactive_zone[self.INIT_Y_POS_INDEX]
                <= comparison_final_y
                <= interactive_zone[self.FINAL_Y_POS_INDEX]
            ):
                interactive_zone[self.INTERACTION_INDEX](
                    init_x_pos=init_x_pos,
                    init_y_pos=init_y_pos,
                    final_x_pos=final_x_pos,
                    final_y_pos=final_y_pos,
                    game_context=game_context,
                )

    def interactive_zone_count(self):
        return len(self._interactive_zones)

    class OverlappingInteractiveZoneException(Exception):
        """ An exception thrown when an interactive zone being registered would overlap
            with a previously registered one."""

        pass


class Button:
    """ An easy to use setup for creating a button interactive zone in the a menu.
    """

    def __init__(
        self,
        init_pos_x,
        init_pos_y,
        final_pos_x,
        final_pos_y,
        interaction,
        button_sprite=None,
        button_animation=None,
    ):
        self.pos_x = init_pos_x
        self.pos_y = init_pos_y
        self.final_pos_x = final_pos_x
        self.final_pos_y = final_pos_y
        self.interaction = interaction

        self.sprite = button_sprite
        self.animation = button_animation

    def _interaction(self, **kwargs):

        # TODO: Play self.animation.
        self.interaction(kwargs)

    def register_with_menu(self, menu: BaseMenu):
        menu.register_interactive_zone(
            self.pos_x,
            self.pos_y,
            self.final_pos_x,
            self.final_pos_y,
            self._interaction,
        )
