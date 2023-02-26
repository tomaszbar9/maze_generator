# Maze Generator

Python code generating rectangular maze with given number of rows and columns.

The maze is drawn using the turtle module. The turtle first draws the longest possible line and after that all branches of the line are drawn, then the branches of each branch, and so on, gradually filling the whole maze up.

The maze generator itself doesn't use recursion, so it can produce a maze of any size, theoretically at least. But when it comes to drawing, the process of finding the longest line is restricted by the limit of recursion. That's why, as the width and height, arguments the program accepts integers between 1 and 100.

The program accepts command-line arguments:

-s, --size `int` `int` (number of cells: width, height, in the range 1 - 100 ; defaults to 40, 20');

-c, --cell `int`(side of one cell in pixels; defaults to 15);

--slow (slow the turtle down);

--close (closes the turtle window when the maze is finished).
