from collections import namedtuple, deque


def tree_maker(points: dict) -> list[deque]:
    """
    Create a list of deques, each deque defining
    coordinates of consecutive points of a line.

    :param dict points: Keys are tuples with coordinates of every point,
        values are sets of tuples with coordinates of neighbouring points.
    :return list[deque]: List to be used by the turtle module as instructions.
    """
    branch = namedtuple("Branch", "line children")
    nodes = {}
    branches = {}
    trunks = []
    queue = deque()

    def reverse_branch(branch: branch) -> None:
        """
        Reverse both items of a branch: line and children.

        :param branch branch: Namedtuple with items:
            'line': deque, 'children': deque.
        """
        branch.line.reverse()
        branch.children.reverse()

    def make_new_branch(point: tuple, points: dict) -> None:
        """
        Create new branch.

        :param tuple point: Coordinates of a starting point.
        :param dict points: Dictionary with all the points.
        """
        next_point = list(points[point])[0]
        new_branch = branch(deque([point, next_point]), deque())
        branches[point] = new_branch

    def make_new_node(point: tuple, points: dict) -> None:
        """
        Create a new node in the `nodes` dictionary.
        The node itself is a dictionary where key is the tuple
        with coordinates of the next point in the given direction
        and the values are None.

        :param tuple point: Coordinates of a node.
        :param dict points: Dictionary with all the points.
        """
        nodes[point] = dict.fromkeys(points[point])

    def extend_line(branch: branch, points: dict) -> None:
        """
        Extend the line of the given branch unitl it hits
        an end of the line or a node.

        :param branch branch: Namedtuple with items:
            'line': deque, 'children': deque.
        :param dict points: Dictionary with all the points.
        """
        line = branch.line
        while len(points[line[-1]]) == 2:
            pair = points[line[-1]]
            for point in pair:
                if point != line[-2]:
                    current = point
            line.append(current)

    def trim(branch: branch) -> branch:
        """
        Compare lengths of all the branches that grow
        from the node at the end of the given branch.
        Choose the longest one and make the others its
        children.

        :param branch branch: Namedtuple with items:
            'line': deque, 'children': deque.
        :return branch: Namedtuple.
        """
        node_coords = branch.line[0]
        node = nodes[node_coords]
        current_branches = [branch for branch in node.values() if branch]
        current_branches.sort(
            key=lambda branch: len(branch.line), reverse=True)
        longest_branch = current_branches[0]
        for branch in current_branches[1:]:
            longest_branch.children.appendleft(branch)
        reverse_branch(longest_branch)
        for direction, value in node.items():
            if not value:
                longest_branch.line.append(direction)
        return longest_branch

    def make_queue(branch: branch) -> list[deque]:
        """
        Make a list of instructions for the turtle.
        First deque defines the line of the given branch,
        then, starting from the beginning, add lines of
        each child, children of its children, and so on.
        Do not start a new branch before the previous is
        finished.

        :param branch branch: One of the two longest branches
            in the maze.
        :return list[deque]: Deques with coordinates
            of consecutive points.
        """
        intructions = deque()
        intructions.append(branch.line)
        branch.children.reverse()
        stack = list(branch.children)
        while stack:
            subbranch = stack.pop()
            intructions.append(subbranch.line)
            if subbranch.children:
                subbranch.children.reverse()
                stack.extend(subbranch.children)
        return intructions
    for point in points:
        neighbours = len(points[point])
        if neighbours == 1:
            make_new_branch(point, points)
        elif neighbours > 2:
            make_new_node(point, points)

    queue.extend(branches.keys())
    while queue:
        coords = queue.pop()
        branch = branches.get(coords)
        if branch:
            extend_line(branch, points)

            node_coords = branch.line[-1]
            if node_coords in branches:
                trunks.append(branch)
                del branches[node_coords]
                continue
            else:
                node = nodes[node_coords]

            reverse_branch(branch)
            node[branch.line[1]] = branch

            number_of_empty_nodes = sum(not val for val in node.values())

            if number_of_empty_nodes == 1:
                new_branch = trim(branch)
                queue.appendleft(new_branch.line[0])

            elif number_of_empty_nodes == 0:
                for branch in node.values():
                    if branch.line[0] != node_coords:
                        reverse_branch(branch)
                        branch.line.popleft()

                longest_branches = sorted(
                    nodes[node_coords].values(),
                    key=lambda x: len(x.line),
                    reverse=True,
                )

                for br in longest_branches[:2]:
                    branches.pop(br.line[-1])

                longest_branches[1].line.popleft()
                longest_branches[0].line.extendleft(
                    longest_branches[1].line)

                if longest_branches[1] not in longest_branches[0].children:
                    longest_branches[0].children.extendleft(
                        longest_branches[1].children
                    )
                else:
                    longest_branches[0].children.remove(
                        longest_branches[1])
                    longest_branches[0].children.extend(
                        longest_branches[2:])

                trunks.append(longest_branches[0])
                trunks.sort(key=lambda x: len(x.line), reverse=True)

    instructions = []
    for trunk in trunks:
        instructions.extend(make_queue(trunk))

    return instructions
