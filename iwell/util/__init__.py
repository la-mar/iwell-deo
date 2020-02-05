import json
import urllib.parse
from typing import Callable, Union, Iterable, Generator, Dict
import itertools

from util.stringprocessor import StringProcessor
from util.jsontools import DateTimeEncoder
from util.itertools_ import query


def urljoin(base: str = "", path: str = "") -> str:
    base = base or ""
    path = path or ""
    if not base.endswith("/"):
        base = base + "/"
    if path.startswith("/"):
        path = path[1:]
    return urllib.parse.urljoin(base, path)


def chunks(iterable: Iterable, n: int = 1000) -> Generator:
    """ Process an infinitely nested interable in chunks of size n (default=1000) """
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)
