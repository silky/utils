import os, sys

vcs_maps = {
        "git": {
            "folder": [".git"],
            "status": "git status",
            "add": "git add",
            "commit": "git commit -am",
            "push": "git push",
            "pull": "git pull",
            },
        "hg":  {
            "folder": [".hg"],
            "status": "hg st", 
            "add": "hg add", 
            "commit": "hg commit -m",
            "push": "hg push",
            "pull": "hg pull",
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
        sys.exit(1) # No version control system found.

    v = vcs_maps[vcs]
    r = 0

    if op == "st":
        r = os.system(v["status"])

    if op == "pl":
        params = ' '.join(sys.argv[2:]).strip(' ')
        r = os.system('%s %s' % (v["pull"], params))

    if op == "pp":
        r = os.system(v["push"])

    if op == "ad":
        r = os.system('%s %s' % (v["add"], ' '.join(sys.argv[2:]).strip(' ')))

    if op == "ci":
        commit_message = '"' + ' '.join(sys.argv[2:]).strip(' ') + '"'
        r = os.system('%s %s' % (v["commit"], commit_message))

    if r > 255:
        # Hmm: http://tldp.org/LDP/abs/html/exitcodes.html
        # Essentially git or whoever has decided to return an error code
        # that is used to make some other decisions; I just want an error
        # though, so that's what we'll do.
        r = 1

    sys.exit(r)

