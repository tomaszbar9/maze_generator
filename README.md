# Maze Generator
Python code generating and drawing a rectangular maze with given number of rows and columns.

The program uses the turtle module for drawing. It treats all the maze's lines as if they were two separate trees or
graphs, and the drawing method follows that idea. First, the "trunks" are found, which are the longest possible line
of each tree. Then, the turtle draws the longer trunk, and the rest of the lines grows from consecutively it as its
branches, gradually filling the whole maze up.

The generator does not use recursion at all, so there is no size limit
(at least when it comes to the program itself).

Since the only third-party libraries used during the development were pytest and pre-commit, the program does not
require any external modules to run.
## Usage
```
git clone https://github.com/tomaszbar9/maze_generator
python -m maze generator [--help] [-s | --size <width> <height>]
                         [-c | --cell <size>] [--slow] [--close]
```
https://user-images.githubusercontent.com/121664530/221419925-5565920b-97e9-4099-a27a-7a287b05a772.mp4
