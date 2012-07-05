#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import ConfigParser


def get_dotshelldb (path=None):
    if not path:
        path = os.getcwd()

    shelldb_file = ".shelldb"
    filepath = os.path.join(path, shelldb_file)

    if os.path.exists(filepath):
        return filepath

    (new, old) = os.path.split(path)

    if not old:
        return None

    return get_dotshelldb(new)


if __name__ == "__main__":
    # Try and find '.shelldb'.
    conf = get_dotshelldb()
    
    if not conf:
        print 'Not .shelldb found in current tree.'
        sys.exit(2)
    
    config = ConfigParser.ConfigParser()
    config.read(conf)
    db = config.get('general', 'db')

    if not db:
        print 'Config file found: %s, but not "db" value in [general].'
        sys.exit(3)

    # Only handle 'select' for now.
    query   = "select %s" % (' '.join(sys.argv[1:]))
    command = 'psql %(db)s -c "%(query)s"' % {'db': db, 'query': query}
     
    # print 'Executing: %s' % command

    r = os.system(command)
    sys.exit(r)
