from .src import parse_args, MazePath, PointsDict, Tree, Instructions
import sys
import turtle

arguments = parse_args(sys.argv[1:])

WIDTH, HEIGHT = arguments.size
STEP = arguments.cell[0]
HOME = -(WIDTH * STEP) // 2, -(HEIGHT * STEP) // 2

maze = MazePath(WIDTH, HEIGHT)
points_dict = PointsDict(maze).get_points_dict()

tree = Tree(points_dict)
instructions = Instructions(tree.trunks)

turtle.hideturtle()
if not arguments.slow:
    turtle.speed(9)
else:
    turtle.speed(1)
for line in instructions:
    turtle.penup()
    for y, x in line:
        x *= STEP
        y *= STEP
        turtle.setposition(x + HOME[0], y + HOME[1])
        turtle.pendown()

if not arguments.close:
    input("Press `enter` to close the turtle window.")
