#!/usr/bin/env python3
"""
Testing for secured_object.py
"""
import pytest
from secured_object.secured_object import Secure

@pytest.fixture
def default():
    return Secure()

def test_default_values(default):
    assert default.x == 100
    assert default.y == 50
    assert default.read_only == 5

def test_default_functions(default):
    assert default.add() == default.x + default.y

def test_mutability(default):
    default.x = 2
    default.y = 5
    assert default.x == 2
    assert default.y == 5

def test_imutable_read_only(default):
    assert default.read_only == 5
    with pytest.raises(AttributeError):
        default.read_only = 6
    assert default.read_only == 5

def test_add_property(default):
    with pytest.raises(AttributeError):
        default.z = 10

def test_dir(default):
    all = dir(default)
    for i in all:
        assert i in [
            '__delattr__', '__dir__', '__getattribute__', '__init__',
            '__setattr__', '__weakref__', 'add', 'look_at_x', 'look_at_y',
            'read_only', 'x', 'y'
            ]

def test_no_internal(default):
    with pytest.raises(AttributeError):
        default.internal