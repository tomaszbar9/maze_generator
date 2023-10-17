from .src import generator, parse_args, MazePath, PointsDict
import sys
import turtle


arguments = parse_args(sys.argv[1:])

WIDTH, HEIGHT = arguments.size
STEP = arguments.cell[0]
HOME = -(WIDTH * STEP) // 2, -(HEIGHT * STEP) // 2

maze = MazePath(WIDTH, HEIGHT)
points = PointsDict(maze)
points_dict = points.get_points_dict()

instructions = generator.tree_maker(points_dict)

print(instructions)

turtle.hideturtle()
if not arguments.slow:
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

if not arguments.close:
    input("Press `enter` to close the turtle window.")
