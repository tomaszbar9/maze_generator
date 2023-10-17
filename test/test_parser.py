from argparse import ArgumentTypeError
import pytest
from src import args_parser


def test_positive_validator_for_string():
    value = args_parser.positive('13')
    assert value == 13


def test_positive_validator_for_int():
    value = args_parser.positive(13)
    assert value == 13


def test_positive_validator_for_negative_str():
    with pytest.raises(ArgumentTypeError):
        args_parser.positive('-13')


def test_parser_with_no_args():
    parser = args_parser.parse_args([])
    assert parser.size == [40, 20]
    assert parser.cell == [15]
    assert not parser.slow
    assert not parser.close


def test_parser_with_args():
    parser = args_parser.parse_args(
        ['-s', '300', '400', '-c', '5', '--slow', '--close'])
    assert parser.size == [300, 400]
    assert parser.cell == [5]
    assert parser.slow
    assert parser.close


def test_parser_with_invalid_args():
    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s', '300'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s', '300', '400', '500'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s', '300', '-1'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s', '-i', '300'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-s', '300', 'zero'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-c'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-c', '-30'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['-c', 'three'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['--slow', '20'])

    with pytest.raises(SystemExit):
        args_parser.parse_args(['--close', '20'])
