import argparse
from collections import namedtuple, deque
import random
import turtle


def main():
    parser = argparse.ArgumentParser("Creates a maze of size s (width height)")
    parser.add_argument(
        "-s",
        "--size",
        help="number of cells: width, height; defaults to 40, 20",
        type=int,
        nargs=2,
        default=[40, 20],
    )
    parser.add_argument(
        "-c",
        "--cell",
        help="side of one cell in pixels; defaults to 15",
        type=int,
        nargs=1,
        default=[15],
    )
    parser.add_argument("--slow", help="slow the turtle down", action="store_true")
    parser.add_argument(
        "--close", help="close the turtle window when finished", action="store_true"
    )
    args = parser.parse_args()

    WIDTH, HEIGHT = args.size
    STEP = args.cell[0]
    HOME = -(WIDTH * STEP) // 2, -(HEIGHT * STEP) // 2

    ### The Maze Section ###
    def create_maze(width: int, height: int) -> dict:
        """
        Create a maze's plan and transform it into a dictionary
        of points that for each point of the maze defines points
        that are connected with it by lines.

        :param int width: Number of horizontal fields in maze.
        :param int height: Number of vertical fields in maze.
        :return dict: Keys are tuples with coordinates of every point,
            values are sets of tuples with coordinates of neighbouring points.
        """

        Cell = namedtuple("Cell", "next prev")
        table = [
            [Cell(next=set(), prev=[]) for _ in range(height)] for _ in range(width)
        ]

        def check_available(address: tuple) -> list:
            """
            Define addresses of four adjacent cells.

            :param tuple address: current cell's coordinates.
            :return list: four tuples with the coordinates.
            """
            x, y = address
            neighbours = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
            available = []
            for w, h in neighbours:
                if w in range(width) and h in range(height) and not table[w][h].prev:
                    available.append((w, h))
            return available

        all_lines = set()
        for row in range(width):
            for col in range(height):
                all_lines.add(((row + 1, col), (row + 1, col + 1)))
                all_lines.add(((row, col + 1), (row + 1, col + 1)))
                if row == 0:
                    all_lines.add(((0, col), (0, col + 1)))
                if col == 0:
                    all_lines.add(((row, 0), (row + 1, 0)))

        # Define each consecutive cell, by the way removing a side line from the all_lines set when the side of the cell is open.
        address = (random.randrange(width), random.randrange(height))
        table[address[0]][address[1]].prev.append(None)
        done = False
        available = check_available(address)
        while not done:
            while available:
                next_field = random.choice(available)

                point_between = max(address[0], next_field[0]), max(
                    address[1], next_field[1]
                )
                if address[0] == next_field[0]:
                    line_between = (
                        point_between,
                        (point_between[0] + 1, point_between[1]),
                    )
                else:
                    line_between = (
                        point_between,
                        (point_between[0], point_between[1] + 1),
                    )
                all_lines.remove(line_between)

                table[next_field[0]][next_field[1]].prev.append(address)
                table[address[0]][address[1]].next.add(next_field)
                address = next_field
                available = check_available(address)

            while not available:
                address = table[address[0]][address[1]].prev[0]
                if address == None:
                    done = True
                    break
                available = check_available(address)

        # Open the maze at both sides of the board.
        enter = ((0, height // 2), (0, height // 2 + 1))
        exit = ((width, height // 2), (width, height // 2 + 1))
        all_lines.remove(enter)
        all_lines.remove(exit)

        points_dict = {}
        for x, y in all_lines:
            for _ in range(2):
                if not x in points_dict:
                    points_dict[x] = {y}
                else:
                    points_dict[x].add(y)
                x, y = y, x
        return points_dict

    ### Drawing Section ###
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
            current_branches.sort(key=lambda branch: len(branch.line), reverse=True)
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
                    longest_branches[0].line.extendleft(longest_branches[1].line)

                    if longest_branches[1] not in longest_branches[0].children:
                        longest_branches[0].children.extendleft(
                            longest_branches[1].children
                        )
                    else:
                        longest_branches[0].children.remove(longest_branches[1])
                        longest_branches[0].children.extend(longest_branches[2:])

                    trunks.append(longest_branches[0])
                    trunks.sort(key=lambda x: len(x.line), reverse=True)

        instructions = []
        for trunk in trunks:
            instructions.extend(make_queue(trunk))

        return instructions

    points_dict = create_maze(WIDTH, HEIGHT)

    instructions = tree_maker(points_dict)

    turtle.hideturtle()
    if not args.slow:
        turtle.speed(9)
    else:
        turtle.speed(1)
    for inst in instructions:
        turtle.penup()
        for x, y in inst:
            x *= STEP
            y *= STEP
            turtle.setposition(x + HOME[0], y + HOME[1])
            turtle.pendown()

    if not args.close:
        input("Press `enter` to close the turtle window.")


if __name__ == "__main__":
    main()
