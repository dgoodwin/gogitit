"""Parses the gogitit manifest."""

import yaml

def load(f):
    data = yaml.safe_load(f)
    print(data)
    m = Manifest(**data)
    # TODO: validation
    print(m.entries[0])

class Manifest:
    def __init__(self, **entries):
        self.__dict__.update(entries)

