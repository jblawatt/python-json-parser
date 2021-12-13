
from functools import partial
from types import NoneType
from typing import Any, Tuple, Union, cast, Callable, Optional


class NothingType: pass

Nothing = NothingType()


JsonValue = Union[
    NothingType,
    None,
    str,
    int,
    float,
    bool,
    list,
    dict
]

ParserResult = Tuple[JsonValue, str]


def parse_char(token: str, text: str) -> ParserResult:
    if not text:
        return (Nothing, "")
    match (text[0], text[1:]):
        case a, rest if a == token:
            return (a, rest)
        case _:
            return (Nothing, text)


def parse_string(token: str, text: str) -> ParserResult:
    match token:
        case "":
            return (Nothing, text)
        case tkn if len(tkn) == 1:
            return parse_char(tkn, text)
        case _:
            match parse_char(token[0], text):
                case NothingType(), _:
                    return (Nothing, text)
                case tkn, rest:
                    match parse_string(token[1:], rest):
                        case NothingType(), _:
                            return (Nothing, text)
                        case string, rest:
                            return (cast(str, tkn) + cast(str, string), rest)


def parser_json_null(text: str) -> ParserResult:
    match parse_string("null", text):
        case "null", rest:
            return (None, rest)
        case _:
            return (Nothing, text)


TokenParseCallable = Callable[[str, str], ParserResult]
ParseCallable = Callable[[str], ParserResult]

def parse_any(parser: TokenParseCallable, text: str, *token: str) -> ParserResult:
    match token:
        case t if len(t) == 1:
            return parser(token[0], text)
        case _:
            match parser(token[0], text):
                case NothingType(), _:
                    return parse_any(parser, text, *t[1:])
                case value, rest:
                    return (value, rest)
                case _:
                    return (Nothing, text)

def parse_all(text: str, *parser: ParseCallable, prev: Optional[str] = None) -> ParserResult:
    if not parser:
        return (Nothing, text)
    match parser[0](text):
        case NothingType(), _:
            return Nothing, text
        case value, rest:
            if len(parser) == 1:
                return (value if prev is None else prev + value, rest)
            return parse_all(rest, *parser[1:], value if prev is None else prev + value)

def parse_boolean(text: str) -> ParserResult:
    match parse_any(parse_string, text, "true", "false"):
        case "true", rest:
            return (True, rest)
        case "false", rest:
            return (False, rest)
        case _:
            return (Nothing, text)


def parse_char_func(func: Callable[[str], bool], text: str) -> ParserResult:
    if not text:
        return (Nothing, "")
    if func(text[0]):
        return (text[0], text[1:])
    return (Nothing, text)


def parse_int(text: str) -> ParserResult:
    match parse_span(str.isdigit, text):
        case NothingType(), _:
            return (Nothing, text)
        case num, rest:
            return int(num), rest


def parse_span(func: Callable[[str], bool], text: str, prev: Optional[JsonValue]=None) -> ParserResult:
    match parse_char_func(func, text):
        case NothingType(), _:
            return (Nothing if prev is None else prev, text)
        case value, rest:
            return parse_span(func, rest, prev=value if prev is None else prev+value)

parse_span_digit = partial(parse_span, func=str.isdigit)

