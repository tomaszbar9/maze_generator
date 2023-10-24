import random
from collections.abc import Generator


class MazePath:
    """ Class containing tools to create a maze's schema represented
    in `fields` attribute as two nested lists.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize an instance.
        :param width: number of fields in a row.
        :param height: number of rows.
        """
        self.width: int = width
        self.height: int = height
        self.fields: list[list[tuple | None]] = [
            [None for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self._current: tuple = ()
        self._set_starting_field()
        self._create_path()

    def _set_starting_field(self) -> None:
        """ Choose randomly a field from all available fields
        and set its value (representing a previous field) to None.
        """
        i, j = random.randrange(self.height), random.randrange(self.width)
        self.fields[i][j] = ()
        self._current = i, j

    def _get_available(self) -> list[tuple[int, int]]:
        """ Get coordinates of fields available to the current_field.
        :return: list of coordinates.
        """
        x, y = self._current
        neighbours = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        available = []
        for n in neighbours:
            if (n[0] in range(self.height) and
                    n[1] in range(self.width) and
                    self.fields[n[0]][n[1]] is None):
                available.append((n[0], n[1]))
        return available

    def _create_path(self) -> None:
        """ Create a path by calling either _step_forward or _step_back function,
        depending on currently available fields. Repeat those steps until
        the path reaches the starting field again.
        """
        if self._current:
            self._step_forward(self._get_available())
            while self._current != ():
                available = self._get_available()
                if available:
                    self._step_forward(available)
                else:
                    self._step_back()

    def _step_forward(self, available: list[tuple[int, int]]) -> None:
        """ Choose randomly one of the available fields as the next field;
        in the `fields` table, assign to the next field the current
        field's coordinates; replace self._current's value with
        the chosen tuple.
        :param available: list of coordinates
        """
        i, j = random.choice(available)
        self.fields[i][j] = self._current
        self._current = i, j

    def _step_back(self) -> None:
        """ Look up the coordinates of the previous field in the fields
        table and assign the found tuple to self._current attribute.
        """
        i, j = self._current
        previous = self.fields[i][j]
        self._current = previous

    def get_pairs(self) -> Generator[tuple[tuple[int, int], tuple[int, int]],
                                     None, None]:
        """ Transform table `fields' into generator of pairs
        containing coordinates of neighbouring fields.
        :return: Generator of pairs of coordinates.
        """
        for i, row in enumerate(self.fields):
            for j, column in enumerate(row):
                yield (i, j), column
