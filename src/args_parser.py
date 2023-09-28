import argparse


def positive(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer.")
    return int_value


def parse_args(args):
    parser = argparse.ArgumentParser("Creates a maze of size s (width height)")
    parser.add_argument(
        "-s",
        "--size",
        help="number of cells: width, height; defaults to 40, 20",
        type=positive,
        nargs=2,
        default=[40, 20],
    )
    parser.add_argument(
        "-c",
        "--cell",
        help="side of one cell in pixels; defaults to 15",
        type=positive,
        nargs=1,
        default=[15],
    )
    parser.add_argument(
        "--slow", help="slow the turtle down", action="store_true")
    parser.add_argument(
        "--close", help="close the turtle window when finished", action="store_true"
    )
    return parser.parse_args(args)
