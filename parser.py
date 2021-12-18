from functools import partial
from types import NoneType
from typing import Any, Tuple, Union, cast, Callable, Optional, Iterable


class NothingType:
    pass


Nothing = NothingType()


JsonValue = Union[NothingType, None, str, int, float, bool, list, dict]

ParserResult = Tuple[JsonValue, str]


def head_split(in_: Iterable) -> Tuple[Any, Any]:
    if not isinstance(in_, (str, list, tuple)):
        in_ = list(in_)
    if len(in_) == 0:
        return None, None
    return in_[0], in_[1:]


hs = head_split


def parse_char(text: str, token: str) -> ParserResult:
    if not text:
        return (Nothing, "")
    match hs(text):
        case a, rest if a == token:
            return (a, rest)
        case _:
            return (Nothing, text)

def parse_char_ignore(text: str, token: str):
    match parse_char(text, token):
        case NothingType(), _:
            return (Nothing, text)
        case _, rest:
            return ("", rest)

def parse_literal(text: str, token: str) -> ParserResult:
    match token:
        case "":
            return (Nothing, text)
        case tkn if len(tkn) == 1:
            return parse_char(text, tkn)
        case _:
            match parse_char(text, token[0]):
                case NothingType(), _:
                    return (Nothing, text)
                case tkn, rest:
                    match parse_literal(rest, token[1:]):
                        case NothingType(), _:
                            return (Nothing, text)
                        case string, rest:
                            return (cast(str, tkn) + cast(str, string), rest)

def parse_string(text: str) -> ParserResult:
    return parse_all(text,
        partial(parse_char_ignore, token="\""),
        partial(parse_span, func=lambda t: t != "\""),
        partial(parse_char_ignore, token="\""),
    )


def parse_null(text: str) -> ParserResult:
    match parse_literal(text, "null"):
        case "null", rest:
            return (None, rest)
        case _:
            return (Nothing, text)


TokenParseCallable = Callable[[str, str], ParserResult]
ParseCallable = Callable[[str], ParserResult]


def parse_any(text: str, *parser: TokenParseCallable) -> ParserResult:
    """return the first parser result tha ist not Nothing"""
    match hs(parser):
        case None, None:
            return (Nothing, text)
        case p, prest:
            match p(text):
                case NothingType(), _:
                    if prest:
                        return parse_any(text, *prest)
                    return (Nothing, text)
                case value, rest:
                    return (value, rest)


parse_literal_true = partial(parse_literal, token="true")
parse_literal_false = partial(parse_literal, token="false")


def parse_boolean(text: str) -> ParserResult:
    match parse_any(text, parse_literal_true, parse_literal_false):
        case "true", rest:
            return (True, rest)
        case "false", rest:
            return (False, rest)
        case _:
            return (Nothing, text)

def strip_char(text: str, token: str):
    match parse_char(text, token):
        case NothingType(), _:
            return text
        case t, rest if t == token:
            return strip_char(rest, token)

def strip_span(text: str, func: Callable):
    match parse_span(text, func):
        case NothingType(), _:
            return text
        case t, rest:
            return strip_span(rest, func)

strip_whitespace = partial(strip_span, func=str.isspace)
strip_comma = partial(strip_span, func=lambda t: t == ",")

def multiple(parser: Callable[[str], ParserResult]):
    def inner(text: str) -> ParserResult:
        match parser(text):
            case NothingType(), _:
                return (Nothing, text)
            case _, rest:
                return inner(rest)
    return inner


def parse_all(text: str, *parser: Callable, prev: str = ""):
    match hs(parser):
        case None, None:
            return (prev if prev else Nothing, text)
        case p, prest:
            match p(text):
                case str() as rest:
                    if prest:
                        return parse_all(rest, *prest, prev=prev)
                    return (prev, rest)
                case NothingType(), _:
                    return (Nothing, prev + text)
                case v, rest:
                    if prest:
                        return parse_all(rest, *prest, prev=prev + v)
                    return (prev + v, rest)


def parse_int(text: str) -> ParserResult:
    match parse_span(text, str.isdigit):
        case NothingType(), _:
            return (Nothing, text)
        case num, rest:
            return (int(num), rest)


def parse_float(text: str) -> ParserResult:
    match parse_all(
            text,
            partial(parse_span, func=str.isdigit),
            partial(parse_char, token="."),
            partial(parse_span, func=str.isdigit),
    ):
        case NothingType(), _:
            return (Nothing, text)
        case value, rest:
            return float(value), rest


def parse_span(
    text: str, func: Callable[[str], bool], prev: Optional[JsonValue] = ""
) -> ParserResult:
    """concat values to span while func applied to char is true"""
    match hs(text):
        case "" | None, _:
            return (prev if prev else Nothing, text)
        case token, rest:
            if func(token):
                return parse_span(rest, func, prev + token)
            return (prev if prev else Nothing, text)
        case _:
            return (Nothing, text)

def apply_to_list(text: str, parser, sep, prev=None) -> ParserResult:
    prev = prev or []
    match parser(text):
        case NothingType(), _:
            return (prev, text)
        case value, rest:
            prev = prev + [value]
            match sep(rest):
                case False, _:
                    return (prev, rest)
                case True, rest:
                    return apply_to_list(rest, parser, sep, prev)

def strip_list_seperator(text: str):
    rest = strip_whitespace(text)
    match parse_char(rest, ","):
        case NothingType(), _:
            return False, text
        case _, rest:
            rest = strip_whitespace(rest)
            return True, rest

def parse_list(text: str) -> ParserResult:
    match parse_char_ignore(text, "["):
        case NothingType(), _:
            return (Nothing, text)
        case _, rest:
            result, rest = apply_to_list(
                rest,
                parse_json_value,
                strip_list_seperator,
                []
            )
            match parse_char_ignore(rest, "]"):
                case NothingType(), _:
                    return (Nothing, text)
                case _, rest:
                    return (result, rest)

def parse_object(text: str, prev = None) -> ParserResult: pass
# def parse_object(text: str, prev = None) -> ParserResult:
#     prev = prev or {}
#     match parse_char_ignore(text, "{"):
#         case NothingType(), _:
#             (Nothing, text)
#         case _, rest:
#             match parse_string(rest):
#                 case NothingType(), _:
#                     return (Nothing, text)
#                 case str() as key, rest:
#                     rest = strip_whitespace(rest)
# 
    

def parse_json_value(text: str):
    return parse_any(
        text,
        parse_null,
        parse_boolean,
        parse_float,
        parse_int,
        parse_string,
        parse_float,
        parse_int,
        parse_list,
    )

