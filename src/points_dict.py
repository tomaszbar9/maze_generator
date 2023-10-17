from collections import defaultdict
from .maze_path import MazePath


class PointsDict:
    def __init__(self, maze_path: MazePath):
        """Initialize an instance.
        :param maze_path: MazePath object.
        """
        self._fields = maze_path.fields
        self._width = maze_path.width
        self._height = maze_path.height
        self.lines = self.get_all_lines() - self.get_open_lines()

    def get_all_lines(self) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        """Create a set of tuples with coordinates of every line in
        the maze's grid.
        :return: set of tuples.
        """
        all_lines = set(((0, column), (0, column + 1))
                        for column in range(self._width))
        all_lines.update(((row, 0), (row + 1, 0))
                         for row in range(self._height))
        for column in range(self._width):
            for row in range(self._height):
                corner = row + 1, column + 1
                all_lines.update({((row + 1, column), corner),
                                  ((row, column + 1), corner)})
        return all_lines

    def get_open_lines(self) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        """Create a set of tuples with coordinates of every line that should
        be removed from the maze's grid.
        :return: set of tuples.
        """
        open_lines = set()
        for i1, row in enumerate(self._fields):
            for j1, previous in enumerate(row):
                if not previous:
                    continue
                i2, j2 = previous
                point_1 = max(i1, i2), max(j1, j2)
                if i1 == i2:
                    point_2 = point_1[0] + 1, point_1[1]
                else:
                    point_2 = point_1[0], point_1[1] + 1
                open_lines.add((point_1, point_2))
        return open_lines

    def get_points_dict(self) -> dict:
        """Transform given pairs into a dictionary where keys are tuples
        with coordinates of points and values are sets containing coordinates
        of points that are connected with their keys by lines.
        :return: dictionary of points and their neighbours.
        """
        points_dict = defaultdict(set)
        for point_1, point_2 in self.lines:
            points_dict[point_1].add(point_2)
            points_dict[point_2].add(point_1)
        return points_dict
