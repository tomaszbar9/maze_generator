import argparse
from argparse import Namespace
from typing import List


def positive(value: str) -> int:
    """ Type validator.
    If given string does not represent a positive inter, raise
    ArgumentTypeError, otherwise return porper integer.
    :param value: string passed to argument parser.
    :return: positive integer.
    """
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer.")
    return int_value


def parse_args(args: List[str]) -> Namespace:
    """ Parse command line arguments.
    :param args:Arguments as a list of strings.
    :return: Namespace object with parsed values
        as attributes.
    """
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
