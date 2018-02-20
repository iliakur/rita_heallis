from datetime import time
from functools import partial
import pytest
import rita_heallis as rita


class MockOut:
    """Captures output."""

    def __init__(self):
        self.outputs = []

    def __call__(self, resp):
        self.outputs.append(resp)


def mock_input(responses):
    """Warning: be careful how many times you run this."""
    r = iter(responses)

    def inner():
        return next(r)

    return inner


def test_pause_for_help():
    mout = MockOut()
    resp = rita.pause_for_help(mock_input(['never']), 'help message', out=mout)

    assert resp == 'never'
    assert mout.outputs == []


def test_pause_for_help_got_help():
    mout = MockOut()
    resp = rita.pause_for_help(mock_input(['h', 'help', 'never']), 'help message', out=mout)

    assert resp == 'never'
    assert mout.outputs == ['help message', 'help message']


def test_help_requested():
    # standard inputs
    assert rita.help_requested("help") == True
    assert rita.help_requested("h") == True
    assert rita.help_requested("help!") == True
    assert rita.help_requested("") == False
    assert rita.help_requested("bob") == False
    # booleans should all be false
    assert rita.help_requested(True) == False
    assert rita.help_requested(False) == False
    # edge cases
    with pytest.raises(TypeError):
        rita.help_requested(None)
    with pytest.raises(TypeError):
        rita.help_requested(0)
    with pytest.raises(TypeError):
        rita.help_requested(4.5)
    with pytest.raises(TypeError):
        rita.help_requested([1, 2])
    with pytest.raises(TypeError):
        rita.help_requested({1: 2})


def test_parse_intervals():
    assert rita.parse_intervals('never') == []

    with pytest.raises(rita.RitaInputError):
        rita.parse_intervals("1 2 3")

    assert rita.parse_intervals("10 15") == [(10, 15)]
    assert rita.parse_intervals("10 15 16 20") == [(10, 15), (16, 20)]


def test_parse_dates():
    assert rita.parse_dates("None") == []
    assert rita.parse_dates("All") == slice(None)

    assert rita.parse_dates("1") == [1]
    assert rita.parse_dates("1 22") == [1, 22]

    with pytest.raises(ValueError):
        rita.parse_dates("test")
