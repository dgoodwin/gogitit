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
        # TODO: repoid must be valid for a directory name as we use it in caches:
        self.id = kwargs['id']
        self.url = kwargs['url']
        self.version = kwargs.get('version', 'master')
        self.transfers = []
        for t in kwargs['transfers']:
            self.transfers.append(Transfer(**t))

    def __str__(self):
        return "Repo<id=%s url=%s version=%s>" % (self.id, self.url, self.version)

class Transfer(object):
    def __init__(self, **kwargs):
        self.src = kwargs['src']
        self.dst = kwargs['dst']

    def __str__(self):
        return "Transfer<src=%s dst=%s>" % (self.src, self.dst)

