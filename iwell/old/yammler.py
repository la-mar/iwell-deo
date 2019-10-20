from __future__ import annotations
from typing import Union, Dict, List, Any
from datetime import datetime, timedelta
import os
import tempfile
from contextlib import contextmanager
import logging
from collections import Counter

import yaml

logger = logging.getLogger(__name__)

from attrdict import AttrDict


class Yammler(AttrDict):
    _no_dump = ["changed"]
    _metavars = ["fspath", "updated_at"]
    _data_key = "data"
    _meta_key = "meta"

    def __init__(self, fspath: str, auto_dump: bool = False, data: dict = None):
        self.fspath = fspath
        self.auto_dump = auto_dump
        self.changed = False
        _yml = None
        with open(fspath) as f:
            _yml = yaml.safe_load(f) or data or {}
        super().__init__(_yml)

    @classmethod
    @contextmanager
    def context(cls, fspath):
        obj = cls(fspath)
        try:
            yield obj
        finally:
            obj.dump(force=True)

    @classmethod
    @contextmanager
    def durable(cls, fspath: str, mode: str = "w+b"):
        """ Safely write to file """
        _fspath = fspath
        _mode = mode
        _file = tempfile.NamedTemporaryFile(_mode, delete=False)

        try:
            yield _file
        except Exception as e:  # noqa
            os.unlink(_file.name)
            raise e
        else:
            _file.close()
            os.rename(_file.name, _fspath)


if __name__ == "__main__":

    y = Yammler("./config/config.yaml")

