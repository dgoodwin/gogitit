"""Parses the gogitit manifest."""

import yaml

def load(f):
    data = yaml.safe_load(f)
    # TODO: validation
    m = Manifest(**data)
    return m

class Manifest(object):
    def __init__(self, **kwargs):
        self.repos = []
        for r in kwargs['repos']:
            self.repos.append(Repo(**r))

class Repo(object):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.source = kwargs['url']
        self.transfers = []
        for t in kwargs['transfers']:
            self.transfers.append(Transfer(**t))

    def __str__(self):
        return "Repo<id=%s url=%s>" % (self.id, self.source)

class Transfer(object):
    def __init__(self, **kwargs):
        self.src = kwargs['src']
        self.dst = kwargs['dst']

    def __str__(self):
        return "Transfer<src=%s dst=%s>" % (self.src, self.dst)

