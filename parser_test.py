import pytest
from functools import partial
from unittest.mock import Mock
from parser import (
    head_split,
    parse_all,
    parse_object,
    parse_span,
    parse_null,
    parse_char,
    parse_literal,
    parse_boolean,
    Nothing,
    NothingType,
    parse_any,
    parse_int,
    parse_float,
    parse_span,
    multiple,
    parse_string,
    parse_list,
    strip_char,
    strip_span,
    strip_whitespace,
    strip_comma,
)

#
# head_split
#
def test_headsplit():
    assert head_split("hello") == ("h", "ello")

def test_headsplit_one():
    assert head_split("h") == ("h", "")

def test_headsplit_empty():
    assert head_split("") == (None, None)

def test_headsplit_objectlist():
    m1 = Mock()
    m2 = Mock()
    assert head_split([m1, m2]) == (m1, [m2])


# 
# parse char
#
def test_parse_char():
    value, rest = parse_char("null", "n")
    assert value == "n"
    assert rest == "ull"

def test_parse_char_empty():
    value, rest = parse_char("", "x")
    assert value == Nothing
    assert rest == ""

# 
# parse literal
#
def test_parse_literal():
    value, rest = parse_literal("helloworld", "hello")
    assert value == "hello"
    assert rest == "world"

def test_parse_literal_not_match():
    value, rest = parse_literal("worldhello", "hello")
    assert value == Nothing
    assert rest == "worldhello"

# 
# parse null
#
def test_parser_json_null():
    value, rest = parse_null("nullfoo")
    assert value is None
    assert rest == "foo"

def test_parser_json_null_nothing():
    value, rest = parse_null("foo")
    assert value == Nothing
    assert rest == "foo"

# 
# parse boolean
#
def test_parse_boolean_true():
    value, rest = parse_boolean("truerest")
    assert value is True
    assert rest == "rest"

def test_parse_boolean_false():
    value, rest = parse_boolean("falserest")
    assert value is False
    assert rest == "rest"

def test_parse_boolean_nothing():
    value, rest = parse_boolean("rest")
    assert value == Nothing
    assert rest == "rest"


# 
# parse any of parser
#
def test_parse_any_first():
    value, rest = parse_any(
        "truevalue", 
        partial(parse_literal, token="true"), 
        partial(parse_literal, token="false"),
    )
    assert value == "true"
    assert rest == "value"

def test_parse_any_second():
    value, rest = parse_any(
        "truevalue", 
        partial(parse_literal, token="false"),
        partial(parse_literal, token="true"), 
    )
    assert value == "true"
    assert rest == "value"


# 
# parse int
#
def test_parse_int():
    value, rest = parse_int("123vier")
    assert value == 123
    assert rest == "vier"

def test_parse_int_nothing():
    value, rest = parse_int("vier567")
    assert value == Nothing
    assert rest == "vier567"

# 
# parse float
#
def test_parse_float():
    value, rest = parse_float("12.34")
    assert value == 12.34
    assert rest == ""

def test_parse_float_nothing():
    text = "12x.34"
    value, rest = parse_float(text)
    assert value == Nothing
    assert rest == text

#
# parse span
#
def test_parse_span():
    value, rest = parse_span("123vier", str.isdigit)
    assert value == "123"
    assert rest == "vier"

def test_parse_span_nothing():
    input_ = "a123vier"
    value, rest = parse_span(input_, str.isdigit)
    assert value == Nothing
    assert rest == input_

def test_parse_span_last():
    input_ = "123"
    value, rest = parse_span(input_, str.isdigit)
    assert value == "123"
    assert rest == ""

#
# parse string
# 
def test_parse_string():
    input_ = '"hello world"'
    value, rest = parse_string(input_)
    assert value == "hello world"
    assert rest == ""

def test_parser_all():
    value, rest = parse_all(
        "12.34asdf", 
        partial(parse_span, func=str.isdigit),
        lambda t: parse_char(t, "."),
        partial(parse_span, func=str.isdigit),
    )
    assert value == "12.34"
    assert rest == "asdf"

def test_parse_all_fail():
    input_ = "12.x34asdf"
    value, rest = parse_all(
        input_,
        partial(parse_span, func=str.isdigit),
        lambda t: parse_char(".", t),
        partial(parse_span, func=str.isdigit),
    )
    assert value == Nothing
    assert rest == input_

def test_parse_all_must():
    value, rest = parse_all(
        " hello      world  restbeginns",
        strip_whitespace,
        partial(parse_literal, token="hello"),
        strip_whitespace,
        partial(parse_literal, token="world"),
        strip_whitespace,
    )

def test_parse_list():
    input_ = '[1, 1.2, null, "hello", true, false]'
    value, rest = parse_list(input_)
    assert value == [1, 1.2, None, "hello", True, False]

def test_parse_nested_lists():
    input_ = '[[1, 2], ["eins", "zwei"], [true, false]]'
    value, rest = parse_list(input_)
    assert value == [[1, 2,], ["eins", "zwei"], [True, False]]

def test_parse_list_invalid():
    input_ = '[1,, 1.2]'
    value, rest = parse_list(input_)
    assert value == Nothing
    assert rest == input_

def test_parse_list_nested_invalid():
    input_ = '[1, [1.2,,true]]'
    value, rest = parse_list(input_)
    assert value == Nothing
    assert rest == input_


def test_parse_list_components():
    input_ = '[1, "hello"]'
    value, rest = parse_char(input_, "[")
    assert value == "["
    assert rest == '1, "hello"]'

    value, rest = parse_int(rest)
    assert value == 1
    assert rest == ', "hello"]'

    _, rest = parse_span(rest, lambda t: t.isspace() or t == ",")
    assert rest == '"hello"]'

    value, rest = parse_string(rest)
    assert value == "hello"
    assert rest == "]"

    value, rest = parse_char(rest, "]")
    assert value == "]"
    assert rest == ""

def test_parser_list_sep():
    input_ = " ,  another"
    value, rest = parse_all(
        input_,
        strip_whitespace,
        strip_comma,
        strip_whitespace,
    )
    assert value == ""
    assert rest == "another"

def test_parse_object():
    input_ = '{"key1": "value1", "key2": 1}'
    value, rest = parse_object(input_)
    assert value["key1"] == "value1"
    assert value["key2"] == 1

def test_foo():
    assert parse_int("1]") == (1, "]")

def test_strip_char():
    assert strip_char("aaaaaab", "a") == "b"

def test_strip_span():
    assert strip_span("      b", str.isspace) == "b"
