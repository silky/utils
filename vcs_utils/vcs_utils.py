import os, sys

vcs_maps = {
        "git": {
            "folder": [".git"],
            "status": "git status",
            "add": "git add",
            "commit": "git commit -am",
            "push": "git push"
            },
        "hg":  {
            "folder": [".hg"],
            "status": "hg st", 
            "add": "hg add", 
            "commit": "hg commit -m",
            "push": "hg push",
            }
        }


def get_vcs (path=None):
    if not path:
        path = os.getcwd()

    for t in vcs_maps:
        for folder in vcs_maps[t]["folder"]:
            if os.path.exists(os.path.join(path, folder)):
                return t

    (new, old) = os.path.split(path)

    if not old:
        return None

    return get_vcs(new)


if __name__ == "__main__":
    op = sys.argv[1]

    vcs = get_vcs()

    if not vcs:
        exit(2) # No version control system found.

    v = vcs_maps[vcs]

    if op == "st":
        os.system(v["status"])

    if op == "pp":
        os.system(v["push"])

    if op == "ad":
        os.system('%s %s' % (v["add"], ' '.join(sys.argv[2:]).strip(' ')))

    if op == "ci":
        commit_message = '"' + ' '.join(sys.argv[2:]).strip(' ') + '"'
        os.system('%s %s' % (v["commit"], commit_message))
