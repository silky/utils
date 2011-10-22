# Find's alll todo items in files sent to it by grep.
# 
# This expects to be called by "find-todo" bash script. It
# calls grep and looks for python files, then reports on
# todo items in there.
#
# Note that the current implementation is designed only
# for python.
#
# Author: Noon Silk <noonsilk@gmail.com>

import io
import os
import sys
import copy
import time
import pickle
import argparse

def process_single_line_comment_todos (f, initial_line, line_number, ttype, comment_token):
    """
        Returns a dictionary with todos and line numbers,
        starting from the given one. Will return 1 or more
        todos.
    """


    line_number  = int(line_number)
    initial_line = initial_line.strip()

    result = []

    with open(f, "r") as sourcef:
        k = 0
        while k < line_number:
            sourcef.readline()
            k = k + 1

        # Now we have lines of interest, so let's look
        # at lines that are still comments.
        
        capturing = False
        captured  = [initial_line]
        
        line = sourcef.readline()
        
        while line:
            line = line.lstrip()
            if not line.startswith(comment_token):
                break

            line = line.lstrip(comment_token + ' ').rstrip()

            # Check to see if it starts with some sort
            # of indicator-of-listed-todo's, like: "-+>N"

            # TODO: Capture number-based lists in this.
 
            if line and (line[0] == '-' or line[0] == '+' or line[0] == '>'):
                line = line.lstrip('-+> ')

                if capturing:
                    # Complete the previous capture
                    result.append({'line': k, 'content': "".join(k + ' ' for k in captured).strip(),
                        'type': ttype })
                    captured = []
                
                captured.append(line.strip('-+> '))
                capturing = True
            else:
                captured.append(line.strip())

            line = sourcef.readline()
            k = k + 1

        result.append({'line': k, 'content': "".join(k + ' ' for k in captured).strip(),
            'type': ttype })

    if len(result) == 0:
        if not initial_line:
            initial_line = "(empty)"

        result.append({ 'line': line_number, 'content': initial_line, 'type': ttype })
    
    return result

# Entrypoint

parser = argparse.ArgumentParser()
parser.add_argument("-path", type=str, help="Path where this is installed.")
args = parser.parse_args()

lines = sys.stdin.readlines()

finfo  = {}
mtimes = {}

try:
    with open("%slast.dat" % args.path, "rb") as p:
        pdata = pickle.load(p)

    if pdata:
        finfo  = pdata[0]
        mtimes = pdata[1]

except Exception as detail:
    #print 'ERROR trying to open last.data'
    pass

largest_number = 0
patterns_file  = "%spatterns" % args.path

with open(patterns_file, "r") as pfile:
    patterns = pfile.readlines()

patterns = [ p.strip() for p in patterns ]
comment_tokens = { 'py': '#', 'tex': '%', 'm': '%' }
anything_modified = False
seen_files = {}

for raw_line in lines:
    splat = raw_line.split(':')
    f     = splat[0]

    if not seen_files.has_key(f):
        seen_files[f] = True

    # see if this file has been modified, and if we should keep processing it.
    this_time = time.ctime(os.path.getmtime(f))

    if mtimes.has_key(f) and this_time <= mtimes[f]:
        # print 'skipping re-processing: %s, len: %s' % (f, len(finfo[f]))
        continue
    else:
        if mtimes.has_key(f) and this_time > mtimes[f]:
            finfo.pop(f)
            mtimes.pop(f)
            anything_modified = True
            
    line_number = splat[1]
    line        = "".join(splat[2:]).strip()

    largest_number = max(largest_number, int(line_number))

    # Ensure this is valid content for the given type

    splat = f.split('.')
    ext   = splat[len(splat) - 1]
    ttype = None

    if ext == "py" or ext == 'tex' or ext == 'm':
        if not line.startswith( comment_tokens[ext] ):
            continue

        line = line.lstrip(comment_tokens[ext] + ' ')
        safe = False
        
        for p in patterns:
            if line.startswith(p):
                safe  = True
                line  = line[len(p):]
                ttype = p

        if not safe:
            continue

        todos = process_single_line_comment_todos(f, line, line_number, ttype, comment_tokens[ext])

    for t in todos:
        if finfo.has_key(f):
            finfo[f].append(t)
        else:
            finfo[f] = [t]

todo_count   = 0
temp_finfo   = copy.deepcopy(finfo)
temp_mtimes  = copy.deepcopy(mtimes)

for f in temp_finfo:
    if( not seen_files.has_key(f) ):
        finfo.pop(f)
        mtimes.pop(f)
        continue

for f in finfo:
    mtimes[f] = time.ctime(os.path.getmtime(f))
    todo_count = todo_count + len(finfo[f])

places = 0
while largest_number > 0:
    largest_number = largest_number / 10
    places = places + 1


if todo_count > 0:
    print 'Summary: %s item(s) to do.' % (todo_count)
    print ''
else:
    print "You're all done!"


keys = finfo.keys()
keys.sort()

k = 0
for f in keys:
    print 'File: %s' % f

    for item in finfo[f]:
        k = k + 1
        print ('  %03d) \t%0' + str(places) + 'd: %s') % (k, int(item["line"]), item["content"])

    print ''

if anything_modified:
    pdata = [finfo, mtimes]
    with open("%slast.dat" % args.path, "wb") as p:
        pickle.dump(pdata, p)
