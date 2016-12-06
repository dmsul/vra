import os

cwd = os.getcwd()

if 'sullivan' in cwd or 'daniel' in cwd:
    DROPBOX = os.path.expanduser('~/Dropbox')
    ROOT_ON_DB = os.path.join(DROPBOX, 'research', 'vra')
else:
    raise NotImplementedError


def data_path(*args):
    return os.path.join('..', 'data', *args)

def out_path(*args):
    return os.path.join(ROOT_ON_DB, 'out', *args)
