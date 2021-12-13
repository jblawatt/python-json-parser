import pytest
from functools import partial
from parser import (
    parse_all,
    parse_char_func,
    parse_span,
    parser_json_null,
    parse_char,
    parse_string,
    parse_boolean,
    Nothing,
    NothingType,
    parse_any,
    parse_int,
    parse_span,
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


def test_parse_char_func():
    value, rest = parse_char_func(str.isdigit, "12test")
    assert value == "1"
    assert rest == "test"


def test_parse_span():
    value, rest = parse_span(str.isdigit, "123vier")
    assert value == "123"
    assert rest == "vier"


def test_parse_int():
    value, rest = parse_int("123vier")
    assert value == 123
    assert rest == "vier"


def test_parser_all():
    value, rest = parse_all(
        "12.34asdf", 
        partial(parse_span, func=str.isdigit),
        lambda t: parse_char(".", t),
        partial(parse_span, func=str.isdigit),
    )
    assert value == "12.34"
    assert rest == "asdf"
