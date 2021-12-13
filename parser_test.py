import pytest
from parser import (
    parser_json_null,
    parse_char,
    parse_string,
    parse_boolean,
    Nothing,
    parse_any,
)


def test_parse_char():
    value, rest = parse_char("n", "null")
    assert value == "n"
    assert rest == "ull"


def test_parse_string():
    value, rest = parse_string("hello", "helloworld")
    assert value == "hello"
    assert rest == "world"


def test_parser_json_null():
    value, rest = parser_json_null("nullfoo")
    assert value is None
    assert rest == "foo"


def test_parser_json_null_nothing():
    value, rest = parser_json_null("foo")
    assert value == Nothing
    assert rest == "foo"


def test_parse_boolean_true():
    value, rest = parse_boolean("truerest")
    assert value is True
    assert rest == "rest"


def test_parse_boolean_false():
    value, rest = parse_boolean("falserest")
    assert value is False
    assert rest == "rest"


def test_parse_any():
    value, rest = parse_any(parse_string, "truevalue", "true", "false")
    assert value == "true"
    assert rest == "value"


def test_parse_boolean_nothing():
    value, rest = parse_boolean("rest")
    assert value == Nothing
    assert rest == "rest"
