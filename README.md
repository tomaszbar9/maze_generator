# Maze Generator

Python code generating rectangular maze with given number of rows and columns.

The maze is drawn using the turtle module. The turtle first draws the longest possible line and after that all branches of the line are drawn, then the branches of each branch, and so on, gradually filling the whole maze up.

The program accepts command-line arguments:

-s, --size `int` `int` (number of cells: width, height; defaults to 40, 20');

-c, --cell `int`(side of one cell in pixels; defaults to 15);

--slow (slow the turtle down);

--close (closes the turtle window when the maze is finished).

https://user-images.githubusercontent.com/121664530/221419925-5565920b-97e9-4099-a27a-7a287b05a772.mp4
