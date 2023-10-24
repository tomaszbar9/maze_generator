from collections import deque
from typing import Self


class Branch:
    def __init__(self,
                 leaf: tuple[int, int],
                 points_dict: dict) -> None:
        """ Initialize an instance.
        :param leaf: tuple with coordinates of an end of a branch.
        :param points_dict: dictionary defining all neighbours of every
            point in the maze: {point: {neighbours}}.
        """
        self.points_dict = points_dict
        self.direction, = points_dict[leaf]
        self.line = deque()
        self.children = deque()
        self.line.append(leaf)
        self.finished = False

    def extend(self) -> None:
        """ Extend the line deque using the values from points_dict until the length
        of a value is other than two.
        """
        point = self.direction
        self.line.append(point)
        while len(self.points_dict[point]) == 2:
            prev = self.line[-2]
            nxt, = (p for p in self.points_dict[point] if p != prev)
            self.line.append(nxt)
            point = nxt
        self.direction = None

    def reverse_(self) -> None:
        """Reverse the branch's attributes: line and children."""
        self.line.reverse()
        self.children.reverse()

    def join_(self, other: Self) -> None:
        """ Join two branches.
        :param other: Branch object.
        """
        other.reverse_()
        self.line.extend(other.line)
        self.children.extend(other.children)
        other.finished = True


class Tree:
    def __init__(self, points_dict: dict) -> None:
        """ Initialize an instance.
        Run methods `get_queue` and 'get_trunks'.
        :param points_dict: dict.
        """
        self.points_dict = points_dict
        self.trunks = list()
        self.nodes = dict()
        self._instructions = None
        self.queue = self.get_queue()
        self.get_trunks()

    def get_queue(self) -> deque[Branch]:
        """ Populate new queue with leaves - ends of branches -
        using the points that have just one neighbour.
        :return: deque of Branch instances.
        """
        result = deque()
        for point, value in self.points_dict.items():
            if len(value) == 1:
                branch = Branch(point, self.points_dict)
                result.append(branch)
        return result

    def new_node(self, key: tuple) -> dict:
        """ Create new value for the `nodes` dictionary.
        :param key: node's coordinates.
        :return: dictionary with keys: "branches" (list of branches)
            and "open_directions" (set of coordinates).
        """
        return {"branches": list(), "open_directions": set(self.points_dict[key])}

    @staticmethod
    def trim(node: dict) -> Branch:
        """ Find the longest branch that is associated with the node, make
        the other objects from the `branches` list its children and mark
        them as finished. Return the parent branch.
        :param node: dictionary with keys: "branches" (list of branches)
            and "open_directions" (set of coordinates).
        :return: Branch object.
        """
        branches = node["branches"]
        branches.sort(key=lambda branch: len(branch.line), reverse=True)
        direction_left, = node["open_directions"]
        parent, *children = branches
        for child in children:
            child.finished = True
            child.reverse_()
            parent.children.append(child)
        parent.direction = direction_left
        return parent

    def move_to_trunks(self, finished_branch) -> None:
        """ Append the finished_branch to the list of trunks. Find in the queue
        a branch that starts where the finished_branch ends and mark it as
        finished. The function runs rarely, only if the first node the given
        branch meets is a leaf.
        :param finished_branch: Branch object.
        """
        self.trunks.append(finished_branch)
        for opposite_branch in self.queue:
            if opposite_branch.line[0] == finished_branch.line[-1]:
                opposite_branch.finished = True

    def get_node(self, branch) -> dict:
        """ Add a new node, if it does not exist to the `nodes` dict.
        Append the branch to it, and remove from open directions a tuple
        that belongs to the branch's line.
        :param branch:
        :return: dictionary with keys: "branches" (list of branches)
            and "open_directions" (set of coordinates).
        """
        last_point = branch.line[-1]
        node = self.nodes.setdefault(last_point, self.new_node(last_point))
        node["branches"].append(branch)
        node["open_directions"].remove(branch.line[-2])
        return node

    def serve(self, branch) -> None:
        """ Extend the branch and pass it to an appropriate function,
        depending on the properties of a node that has the same coordinates
        as the last point of the branch's line.
        If the last point has just one neighbour, pass the branch to trunks.
        Otherwise, add the branch to a node and:
            - if there is only one open direction left in the node's
                open_directions set, trim the branch and put it at the
                beginning of the que.
            - if no open directions left, join the branch with the longest
                one from the node's "branches" list, and pass it to
                the trunks.
        :param branch: Branch object.
        """
        branch.extend()
        if len(self.points_dict[branch.line[-1]]) == 1:
            self.move_to_trunks(branch)
        else:
            node = self.get_node(branch)
            directions_left = len(node["open_directions"])
            if directions_left == 1:
                branch = self.trim(node)
                self.queue.appendleft(branch)
            elif not directions_left:
                branch.join_(node["branches"][0])
                self.trunks.append(branch)

    def get_trunks(self) -> None:
        """ Iterate through the queue and pass unfinished branches
        to the `serve` method.
        """
        while self.queue:
            branch = self.queue.pop()
            if not branch.finished:
                self.serve(branch)


class Instructions:
    """ Iterator returning instructions for the turtle module.
    First yields the coordinates of the line of the longest branch
    (one of two trunks), then lines of its consecutive children
    and so on. After the longest branch and its children are
    exhausted, iterator returns by the same way the other trunk.
    """

    def __init__(self, trunks: list):
        self._queue = trunks

    def __iter__(self):
        return self

    def __next__(self) -> deque:
        if not self._queue:
            raise StopIteration
        next_branch = self._queue.pop()
        if next_branch.children:
            self._queue.extend(list(reversed(next_branch.children)))
        return next_branch.line
