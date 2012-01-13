import os

vcs_maps = {
        "git": {"status": "git status"},
        "hg":  {"status": "hg st"}
        }

def command_st ():
    vcs = get_vcs()

    if vcs:
        os.system(vcs_maps[vcs]["status"])
    else:
        exit(2)


def get_vcs (path=None):
    if not path:
        path = os.getcwd()

    maps = {"git": [".git"], "hg": [".hg"], "svn": [".svn"] }

    for t in maps:
        for folder in maps[t]:
            if os.path.exists(os.path.join(path, folder)):
                return t

    (new, old) = os.path.split(path)

    if not old:
        return None

    return get_vcs(new)


if __name__ == "__main__":
    command_st()
