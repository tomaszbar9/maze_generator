import pytest
from src import MazePath, PointsDict


def test_get_all_lines():
    mp_6 = MazePath(2, 3)
    pd_6 = PointsDict(mp_6)
    assert set(pd_6.get_all_lines()) == {
        ((0, 0), (0, 1)), ((0, 1), (0, 2)),
        ((0, 0), (1, 0)), ((0, 1), (1, 1)), ((0, 2), (1, 2)),
        ((1, 0), (1, 1)), ((1, 1), (1, 2)),
        ((1, 0), (2, 0)), ((1, 1), (2, 1)), ((1, 2), (2, 2)),
        ((2, 0), (2, 1)), ((2, 1), (2, 2)),
        ((2, 0), (3, 0)), ((2, 1), (3, 1)), ((2, 2), (3, 2)),
        ((3, 0), (3, 1)), ((3, 1), (3, 2))
    }


# List of adjacent pairs:
# [((0, 0), (1, 0)), ((0, 1), (0, 0)), ((0, 2), (0, 1)),
#  ((1, 0), (1, 1)), ((1, 1), (2, 1)), ((1, 2), (0, 2)),
#  ((2, 0), (3, 0)), ((2, 1), (2, 0)), ((2, 2), (1, 2)),
#  ((3, 0), (    )), ((3, 1), (3, 2)), ((3, 2), (2, 2))]
def test_get_open_lines():
    mp_12 = MazePath(3, 4)
    mp_12.fields = [[(1, 0), (0, 0), (0, 1)],
                    [(1, 1), (2, 1), (0, 2)],
                    [(3, 0), (2, 0), (1, 2)],
                    [(), (3, 2), (2, 2)]]
    pd_12 = PointsDict(mp_12)
    assert set(pd_12.get_open_lines()) == {
        ((1, 0), (1, 1)), ((0, 1), (1, 1)), ((0, 2), (1, 2)),
        ((1, 1), (2, 1)), ((2, 1), (2, 2)), ((1, 2), (1, 3)),
        ((3, 0), (3, 1)), ((2, 1), (3, 1)), ((2, 2), (2, 3)),
        ((3, 2), (4, 2)), ((3, 2), (3, 3)),
    }


@pytest.mark.parametrize("size, exits",
                         [((10, 5), {((2, 0), (3, 0)), ((2, 10), (3, 10))}),
                          ((10, 6), {((3, 0), (4, 0)), ((3, 10), (4, 10))}),
                          ((1, 1), {((0, 0), (1, 0)), ((0, 1), (1, 1))})])
def test_get_exits(size, exits):
    maze = MazePath(10, 10)
    pd = PointsDict(maze)
    pd._width, pd._height = size
    assert pd.get_exits_lines() == exits


def test_get_points_dict():
    lines = (((0, 0), (0, 1)), ((0, 0), (1, 0)),
             ((0, 1), (0, 2)), ((0, 2), (1, 2)),
             ((1, 0), (1, 1)), ((1, 0), (2, 0)),
             ((1, 2), (2, 2)), ((2, 0), (3, 0)),
             ((2, 1), (2, 2)), ((2, 2), (3, 2)),
             ((3, 0), (3, 1)), ((3, 1), (3, 2)))
    points_dict = {(0, 0): {(0, 1), (1, 0)},
                   (0, 1): {(0, 0), (0, 2)},
                   (0, 2): {(0, 1), (1, 2)},
                   (1, 0): {(0, 0), (1, 1), (2, 0)},
                   (1, 1): {(1, 0)},
                   (1, 2): {(0, 2), (2, 2)},
                   (2, 0): {(1, 0), (3, 0)},
                   (2, 1): {(2, 2)},
                   (2, 2): {(1, 2), (2, 1), (3, 2)},
                   (3, 0): {(2, 0), (3, 1)},
                   (3, 1): {(3, 0), (3, 2)},
                   (3, 2): {(2, 2), (3, 1)}}
    maze = MazePath(10, 10)
    pd = PointsDict(maze)
    pd.lines = lines
    assert pd.get_points_dict() == points_dict