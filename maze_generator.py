import argparse
import random
from collections import namedtuple, deque
import turtle


parser = argparse.ArgumentParser("Creates a maze of size s (width height)")
parser.add_argument(
    "-s",
    "--size",
    help="number of cells: width, height, in the range 1 - 100 ; defaults to 40, 20",
    type=int,
    nargs=2,
    choices=range(1, 101),
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

Cell = namedtuple("Cell", "next prev")
table = [[Cell(next=set(), prev=[]) for _ in range(HEIGHT)] for _ in range(WIDTH)]


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
        if w in range(WIDTH) and h in range(HEIGHT) and not table[w][h].prev:
            available.append((w, h))
    return available


all_lines = set()
for row in range(WIDTH):
    for col in range(HEIGHT):
        all_lines.add(((row + 1, col), (row + 1, col + 1)))
        all_lines.add(((row, col + 1), (row + 1, col + 1)))
        if row == 0:
            all_lines.add(((0, col), (0, col + 1)))
        if col == 0:
            all_lines.add(((row, 0), (row + 1, 0)))

# Define each consecutive cell, by the way removing a side line from the all_lines set when the side of the cell is open.
address = (random.randrange(WIDTH), random.randrange(HEIGHT))
table[address[0]][address[1]].prev.append(None)
done = False
available = check_available(address)
while not done:
    while available:
        next_field = random.choice(available)

        point_between = max(address[0], next_field[0]), max(address[1], next_field[1])
        if address[0] == next_field[0]:
            line_between = (point_between, (point_between[0] + 1, point_between[1]))
        else:
            line_between = (point_between, (point_between[0], point_between[1] + 1))
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
enter = ((0, HEIGHT // 2), (0, HEIGHT // 2 + 1))
exit = ((WIDTH, HEIGHT // 2), (WIDTH, HEIGHT // 2 + 1))
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


### Drawing Section ###

all_paths = []
checked_singles = set()
nodes_dict = {}
instructions = []
lines_disconnected = []


def follow_the_line(node: tuple, next_point: tuple) -> tuple[int, int]:
    """Recursively follow a line starting from a given `node` point.
    Add to the `all_paths` list deque of points belonging to a stretch between two nodes.
    To each node in the `nodes_dict` add as a value list of dictionaries describing parameters
    of a single stretch in each direction.
    :param tuple node: Coordinates of a starting point of a stretch.
    :param tuple next_point: Coordinates of a subsequent point.
    :return tuple: Length of the stretch; index pointing to 
        the corresponding deque in the `all_paths` list.
    """
    entry_point = node
    current_path = deque((node, next_point))
    while len(points_dict[next_point]) == 2:
        points_dict[next_point].remove(node)
        node = next_point
        next_point = points_dict[next_point].pop()
        current_path.append(next_point)

    all_paths.append(current_path)
    current_path_index = len(all_paths) - 1
    current_path_length = len(current_path) - 1
    if len(points_dict[next_point]) == 1:
        if entry_point in checked_singles:
            nodes_dict[entry_point] = [
                {
                    "length": current_path_length,
                    "path_index": current_path_index,
                    "other_end": current_path[-1],
                }
            ]
        checked_singles.add(next_point)
    else:
        nodes_dict[next_point] = [
            {
                "length": current_path_length,
                "path_index": current_path_index,
                "other_end": entry_point,
            }
        ]
        for point in points_dict[next_point]:
            if point != node:
                length, idx = follow_the_line(next_point, point)
                nodes_dict[next_point].append(
                    {
                        "length": length,
                        "path_index": idx,
                        "other_end": all_paths[idx][-1],
                    }
                )
    return current_path_length, current_path_index


def find_longest_lines(node: tuple, prev: tuple = ()) -> int:
    """
    Recursively find longest possible lines for a given node.
    :param tuple node: Coordinates of a node.
    :param tuple prev: Coordinates of a previous node
        (for internal use of the function only), defaults to ().
    :return int: Sum of the two longest paths from the node.
    """
    longest = 0
    if node not in nodes_dict:
        return 0
    if len(nodes_dict[node]) == 1:
        lines_disconnected.append(nodes_dict[node][0])
        return nodes_dict[node][0]["length"]
    for direction in nodes_dict[node]:
        if direction["other_end"] == prev:
            continue
        this_longest = direction["length"] + find_longest_lines(
            direction["other_end"], node
        )
        direction["longest"] = this_longest
        longest = max(longest, this_longest)
    if prev:
        return longest
    else:
        current_node = nodes_dict[node]
        current_node.sort(key=lambda x: x["longest"])
        total = current_node[-1]["longest"] + current_node[-2]["longest"]
        return total


def make_instructions(node: tuple, path_index: int) -> None:
    """Recursively add lists of coordinates of each line
    (starting from the longest one) to `instructions` list.
    :param tuple node: Coordinates of a node.
    :param int path_index: Index of a deque with coordinates in
        `all_paths` list.
    """
    new_list = []
    instructions.append(new_list)
    while True:
        new_points_list = all_paths[path_index]
        prev = node
        if new_points_list[0] != prev:
            new_points_list.reverse()
        if new_list:
            new_points_list.popleft()
        new_list.extend(new_points_list)
        if new_list[-1] not in nodes_dict:
            break
        node = new_list[-1]
        node_length = len(nodes_dict[node])
        for idx, line in enumerate(reversed(nodes_dict[node])):
            if line["other_end"] == prev:
                del nodes_dict[node][node_length - idx - 1]
                break
        line = nodes_dict[node].pop()
        path_index = line["path_index"]
        while nodes_dict[node]:
            line = nodes_dict[node].pop()
            next_path_index = line["path_index"]
            make_instructions(node, next_path_index)


for point in points_dict:
    if len(points_dict[point]) == 1 and point not in checked_singles:
        next_point = points_dict[point].pop()
        checked_singles.add(point)
        follow_the_line(point, next_point)

longests_paths = []
for node in nodes_dict:
    longests_paths.append((find_longest_lines(node), node))

longests_paths.sort()

# Find an edge point (choosing a shorter way from a given point).
for starting_point in reversed(longests_paths):
    current_point = starting_point[1]
    if current_point in nodes_dict and len(nodes_dict[current_point]) > 0:
        prev = current_point
        edge_node = nodes_dict[prev][-2]["other_end"]
        path_index = nodes_dict[prev][-2]["path_index"]
        while edge_node in nodes_dict:
            for index in range(-1, -3, -1):
                next_node = nodes_dict[edge_node][index]["other_end"]
                path_index = nodes_dict[edge_node][index]["path_index"]
                if next_node != prev:
                    prev = edge_node
                    edge_node = next_node
                    break
        make_instructions(edge_node, path_index)

for line in lines_disconnected:
    instructions.append(all_paths[line["path_index"]])

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
