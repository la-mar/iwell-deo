def query(path: str, data: dict, sep: str = "."):
    """ Query any combination of nested lists/dicts """
    elements = path.split(sep)
    for e in elements:
        if issubclass(type(data), list) and len(data) > 0:
            data = data[int(e)]  # TODO: this needs to be smarter
        elif issubclass(type(data), dict):
            data = data.get(e, {})

    return data if data != {} else None
