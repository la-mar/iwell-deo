import json
import urllib.parse
from typing import Callable, Union, Tuple

from util.stringprocessor import StringProcessor
from util.jsontools import DateTimeEncoder


def urljoin(base: str = "", path: str = "") -> str:
    base = base or ""
    path = path or ""
    if not base.endswith("/"):
        base = base + "/"
    if path.startswith("/"):
        path = path[1:]
    return urllib.parse.urljoin(base, path)
