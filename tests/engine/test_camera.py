import pytest

from thegame.engine import Map
from thegame.engine.camera import Camera


@pytest.mark.parametrize(
    "camera_width, camera_height, output_sheet",
    [
        (5, 3, [[None, 1, 1, 1, None], [None, 1, 1, 1, None], [None, 1, 1, 1, None]]),
        (
            7,
            3,
            [
                [None, None, 1, 1, 1, None, None],
                [None, None, 1, 1, 1, None, None],
                [None, None, 1, 1, 1, None, None],
            ],
        ),
        (
            9,
            3,
            [
                [None, None, None, 1, 1, 1, None, None, None],
                [None, None, None, 1, 1, 1, None, None, None],
                [None, None, None, 1, 1, 1, None, None, None],
            ],
        ),
        (
            3,
            5,
            [[None, None, None], [1, 1, 1], [1, 1, 1], [1, 1, 1], [None, None, None]],
        ),
        (
            3,
            7,
            [
                [None, None, None],
                [None, None, None],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [None, None, None],
                [None, None, None],
            ],
        ),
        (
            3,
            9,
            [
                [None, None, None],
                [None, None, None],
                [None, None, None],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [None, None, None],
                [None, None, None],
                [None, None, None],
            ],
        ),
        (3, 3, [[1, 1, 1], [1, 1, 1], [1, 1, 1]]),
        (1, 1, [[1]]),
        (
            5,
            5,
            [
                [None, None, None, None, None],
                [None, 1, 1, 1, None],
                [None, 1, 1, 1, None],
                [None, 1, 1, 1, None],
                [None, None, None, None, None],
            ],
        ),
        (
            7,
            7,
            [
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
                [None, None, 1, 1, 1, None, None],
                [None, None, 1, 1, 1, None, None],
                [None, None, 1, 1, 1, None, None],
                [None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None],
            ],
        ),
    ],
)
def test_camera_fov_produces_borders_and_reduces_map(
    camera_width, camera_height, output_sheet
):

    # camera_x,y = (1, 1). This positions the camera in the center of the 3x3 map, no matter what the
    # actual camera width and height are.
    camera = Camera(
        camera_width=camera_width, camera_height=camera_height, camera_x=1, camera_y=1
    )
    sheet = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    test_map = Map(list(sheet), list(sheet), list(sheet), list(sheet), validate=False)

    fov = camera.get_camera_fov(test_map)

    assert fov == [output_sheet, output_sheet, output_sheet, output_sheet]
