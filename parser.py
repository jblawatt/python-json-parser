
from types import NoneType
from typing import Any, Tuple, Union, cast, Callable


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
                case tkn, rest if isinstance(tkn, str):
                    match parse_string(token[1:], rest):
                        case string, rest if isinstance(string, str):
                            return (cast(str, tkn) + cast(str, string), rest)
                        case _:
                            return (Nothing, text)
                case _:
                    return (Nothing, text)


def parser_json_null(text: str) -> ParserResult:
    match parse_string("null", text):
        case "null", rest:
            return (None, rest)
        case _:
            return (Nothing, text)


TokenParseCallable = Callable[[str, str], ParserResult]

def parse_any(parser: TokenParseCallable, text: str, *token: str) -> ParserResult:
    match token:
        case t if len(t) == 1:
            return parser(token[0], text)
        case _:
            match parser(token[0], text):
                case nothing, _ if nothing == Nothing:
                    return parse_any(parser, text, *t[1:])
                case value, rest:
                    return (value, rest)
                case _:
                    return (Nothing, text)


def parse_boolean(text: str) -> ParserResult:
    match parse_any(parse_string, text, "true", "false"):
        case "true", rest:
            return (True, rest)
        case "false", rest:
            return (False, rest)
        case _:
            return (Nothing, text)

