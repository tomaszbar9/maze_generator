import pytest
from unittest.mock import patch
from src import MazePath

WIDTH, HEIGHT = 5, 6


@patch('src.MazePath._create_path')
def test_starting_point(_muted_create_path):
    starting_point = ()
    maze = MazePath(WIDTH, HEIGHT)
    for row_index, row in enumerate(maze.fields):
        for column_index, column in enumerate(row):
            if column is not None:
                starting_point = row_index, column_index
                break
        if starting_point:
            break
    assert maze.fields[starting_point[0]][starting_point[1]] == ()


class TestAvailable:

    #      0     1     2     3     4
    # 0  (cur) (0,2) (0,3) (0,4) (1,4)
    # 1  None  (0,1) (1,1) (cur) (2,4)
    # 2  None  (cur)(start)(2,2) (2,3)
    # 3  None  None  None  None  (cur)
    # 4  None  None  (cur) None  None
    # 5  None  (cur) None  None  (cur)

    @pytest.fixture(scope='class')
    @patch('src.MazePath._set_starting_field')
    def maze(self, muted_starting_field_function):
        mock_maze = MazePath(5, 6)
        mock_maze.fields[2][2] = ()
        mock_maze.fields[2][3] = 2, 2
        mock_maze.fields[2][4] = 2, 3
        mock_maze.fields[1][4] = 2, 4
        mock_maze.fields[0][4] = 1, 4
        mock_maze.fields[0][3] = 0, 4
        mock_maze.fields[0][2] = 0, 3
        mock_maze.fields[0][1] = 0, 2
        mock_maze.fields[1][1] = 0, 1
        mock_maze.fields[1][2] = 1, 1
        return mock_maze

    @pytest.mark.parametrize("current_field, available_fields",
                             [((0, 0), [(1, 0)]),
                              ((1, 3), []),
                              ((2, 1), [(2, 0), (3, 1)]),
                              ((3, 4), [(3, 3), (4, 4)]),
                              ((4, 2), [(3, 2), (4, 3), (5, 2), (4, 1)]),
                              ((5, 1), [(4, 1), (5, 2), (5, 0)]),
                              ((5, 4), [(4, 4), (5, 3)]),
                              ])
    def test_get_available(self, maze, current_field, available_fields):
        maze._current = current_field
        assert set(maze._get_available()) == set(available_fields)


@patch('src.MazePath._step_forward')
@patch('src.MazePath._get_available')
@patch('src.MazePath._set_starting_field')
def test_create_path(muted_starting_field,
                     mock_available,
                     mock_forward):
    m = MazePath(WIDTH, HEIGHT)
    current_fields = iter(((1, 0), (1, 0), (1, 0), ()))

    def change_current():
        m._current = next(current_fields)

    mock_available.side_effect = [[(3, 2), (4, 3), (5, 2), (4, 1)],
                                  [(4, 1), (5, 2), (5, 0)], [],
                                  [(4, 4), (5, 3)], [],
                                  [(1, 0)], [], []]

    with patch('src.MazePath._step_back', wraps=change_current) as mock_back:
        mock_forward.reset_mock()
        mock_back.reset_mock()
        m._current = 0, 0
        m._create_path()
        assert mock_forward.call_count == 4
        assert mock_back.call_count == 4


@pytest.mark.parametrize("available",
                         [[(3, 2), (4, 3), (5, 2), (4, 1)],
                          [(4, 1), (5, 2), (5, 0)],
                          [(4, 4), (5, 3)],
                          [(1, 0)]])
def test_forward(available):
    m = MazePath(WIDTH, HEIGHT)
    m._current = (0, 0)
    m._step_forward(available)
    i, j = m._current
    assert m._current in available
    assert m.fields[i][j] == (0, 0)


def test_backward():
    m = MazePath(WIDTH, HEIGHT)
    m._current = (4, 4)
    m.fields[4][4] = (4, 3)
    m._step_back()
    assert m._current == (4, 3)


def test_get_pairs_valid():
    m = MazePath(WIDTH, HEIGHT)
    m.fields = [[(0, 1), (1, 1)],
                [(0, 0), ()]]
    pairs = [((0, 0), (0, 1)), ((0, 1), (1, 1)),
             ((1, 0), (0, 0)), ((1, 1), ())]
    assert set(m.get_pairs()) == set(pairs)
