""" Unit tests for the base menu object. """

from unittest.mock import Mock

import pytest

from thegame.engine import BaseMenu, Button


def get_base_menu():
    # TODO: Once actual image loading has been implemented
    # this mock should probably have some return values.
    return BaseMenu(Mock())


def interaction():
    """ A no-op method for an interaction. """
    pass


def test_get_interactive_zones_returns_all_interactive_zone():
    menu = get_base_menu()

    zone_one = (0, 0, 0, 0, interaction)
    zone_two = (1, 1, 1, 1, interaction)
    zone_three = (2, 2, 2, 2, interaction)
    zone_four = (3, 3, 3, 3, interaction)

    menu.register_interactive_zone(*zone_one)
    menu.register_interactive_zone(*zone_two)
    menu.register_interactive_zone(*zone_three)
    menu.register_interactive_zone(*zone_four)

    interactive_zones = menu.get_interactive_zones()

    assert zone_one in interactive_zones
    assert zone_two in interactive_zones
    assert zone_three in interactive_zones
    assert zone_four in interactive_zones
    assert len(interactive_zones) == 4


def test_get_interactive_zones_cannot_alter_interactive_zones():
    menu = get_base_menu()
    zone = (0, 0, 0, 0, interaction)
    menu.register_interactive_zone(*zone)

    interactive_zones = menu.get_interactive_zones()
    interactive_zones.clear()

    assert len(menu.get_interactive_zones()) > 0


@pytest.mark.parametrize(
    "input_zone, output_zone",
    [
        ((0, 0, 1, 1, interaction), (0, 0, 1, 1, interaction)),
        ((0, 1, 1, 0, interaction), (0, 0, 1, 1, interaction)),
        ((1, 1, 0, 0, interaction), (0, 0, 1, 1, interaction)),
        ((1, 0, 0, 1, interaction), (0, 0, 1, 1, interaction)),
    ],
)
def test_register_interactive_zone(input_zone, output_zone):

    menu = get_base_menu()

    menu.register_interactive_zone(*input_zone)

    assert output_zone in menu.get_interactive_zones()


@pytest.mark.parametrize(
    "zone_one, zone_two",
    [
        ((0, 0, 4, 4, interaction), (1, 1, 3, 3, interaction)),
        ((2, 2, 4, 4, interaction), (1, 1, 3, 3, interaction)),
        ((1, 1, 1, 1, interaction), (0, 0, 1, 1, interaction)),
        ((4, 4, 0, 0, interaction), (1, 1, 3, 3, interaction)),
        ((4, 4, 2, 2, interaction), (3, 3, 1, 1, interaction)),
        ((1, 1, 1, 1, interaction), (1, 1, 0, 0, interaction)),
        ((1, 1, 3, 3, interaction), (0, 0, 4, 4, interaction)),
        ((3, 3, 1, 1, interaction), (4, 4, 0, 0, interaction)),
        ((3, 3, 1, 1, interaction), (0, 0, 4, 4, interaction)),
        ((1, 1, 3, 3, interaction), (4, 4, 0, 0, interaction)),
    ],
)
def test_registering_interactive_zone_within_interactive_zone_raises_exception(
    zone_one, zone_two
):
    """ Test that registering a zone within a zone raises an exception """

    menu = get_base_menu()
    menu.register_interactive_zone(*zone_one)

    with pytest.raises(BaseMenu.OverlappingInteractiveZoneException):
        menu.register_interactive_zone(*zone_two)


def test_call_interactive_zone_by_index_calls_correct_interaction():

    interaction_mock = Mock
    menu = get_base_menu()
    menu.register_interactive_zone(0, 0, 0, 0, interaction)
    menu.register_interactive_zone(1, 1, 1, 1, interaction_mock)

    menu.call_interactive_zone_by_index(1, Mock())

    assert interaction_mock.called


def test_interaction_can_call_game_context():
    """ Test that when an interaction is called it has access to game context."""

    def game_interaction(game_context):
        game_context.call()

    context = Mock()
    menu = get_base_menu()
    menu.register_interactive_zone(0, 0, 0, 0, game_interaction)

    menu.call_interactive_zone_by_index(0, context)

    assert context.call.called


@pytest.mark.parametrize(
    "click",
    [
        (0, 1, 1, 2),
        (0, 1, 2, 1),
        (1, 0, 1, 2),
        (1, 0, 2, 1),
        (1, 2, 0, 1),
        (2, 1, 0, 1),
        (1, 2, 1, 0),
        (2, 1, 1, 0),
    ],
)
def test_clicking_interactive_zone_calls_interaction(click):

    interaction_mock = Mock()

    menu = get_base_menu()
    menu.register_interactive_zone(0, 0, 2, 2, interaction_mock)

    menu.call_interactive_zone_by_click(*click, Mock())

    assert interaction_mock.called


@pytest.mark.parametrize(
    "click",
    [
        (0, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 2, 2),
        (2, 2, 1, 1),
        (0, 0, 2, 2),
        (2, 2, 0, 0),
    ],
)
def test_click_not_starting_or_not_ending_in_button_do_not_call_interaction(click):

    interaction_mock = Mock()

    menu = get_base_menu()
    menu.register_interactive_zone(1, 1, 1, 1, interaction_mock)

    menu.call_interactive_zone_by_click(*click, Mock())

    assert not interaction_mock.called


def test_interactive_zone_count_returns_correct_count():
    menu = get_base_menu()
    menu.register_interactive_zone(0, 0, 0, 0, interaction)
    menu.register_interactive_zone(1, 1, 1, 1, interaction)
    menu.register_interactive_zone(2, 2, 2, 2, interaction)

    count = menu.interactive_zone_count()

    assert count == 3


def test_button_registers_interactive_zone_correctly():

    button = Button(0, 0, 1, 1, interaction)
    menu = get_base_menu()

    button.register_with_menu(menu)

    assert (0, 0, 1, 1, button._interaction) in menu.get_interactive_zones()


def test_button_clicked_calls_interaction():

    interaction_mock = Mock()
    button = Button(0, 0, 1, 1, interaction_mock)
    menu = get_base_menu()
    button.register_with_menu(menu)

    menu.call_interactive_zone_by_click(0, 0, 1, 1, Mock())

    assert interaction_mock.called
