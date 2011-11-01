# Find's alll todo items in files sent to it by grep.
# 
# This expects to be called by "find-todo" bash script. It
# calls grep and looks for python files, then reports on
# todo items in there.
#
# Note that the current implementation is designed only
# for single-line comment languages.
#
# Author: Noon Silk <noonsilk@gmail.com>
#
# Usage:
#
#   When passed -output=concise, the list of todos can
#   be fed into vim, say perhaps
#
#       :cgetbuffer [bufN]
#       :cope
#   
#   i.e. you should consider a command to call your
#   script, with this output type, and then open up
#   the resulting buffer.
#
#   or alternatively
#
#   Command to get this list to show up in quickfix:
#   execute "!/home/noon/dev/silky-github/utils/find-todo/find-todo ~/dev/
#   concise>~/temp/foo.err" | cget ~/temp/foo.err | copen<CR>
#
#   I've mapped something like this to be a command in my
#   vimrc: command Gtt execute "...."
#
#   Revised expression is:
#
#   cgetexpr system("find-todo . concise")
#
#   TODO: Bug when handling multiple todo's with the same prefix. That is,
#       I need to fix the prefix handling in general.

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
        
        capturing  = False
        captured   = [initial_line]
        line_start = k
        
        line = sourcef.readline()
        
        while line:
            line = line.lstrip()
            if not line.startswith(comment_token):
                break

            line = line.lstrip(comment_token + ' ').rstrip()

            # Check to see if it starts with some sort
            # of indicator-of-listed-todo's, like: "-+>N"

            # TODO: Capture number-based lists in this.

            if not line and capturing:
                # TODO:
                #   Consider looking ahead to see if the next line actually starts
                #   with one of the valid tokens (perhaps the current one), and if
                #   so we can consider that to be an item as well.

                # Complete the previous capture
                result.append({'line': line_start, \
                            'content': "".join(k + ' ' for k in captured).strip(),
                        'type': ttype })
                captured = []
                break # We're done.
 
            if line and (line[0] == '-' or line[0] == '+' or line[0] == '>'):
                line = line.lstrip('-+> ')

                if capturing:
                    # Complete the previous capture
                    result.append({'line': line_start, \
                            'content': "".join(k + ' ' for k in captured).strip(),
                        'type': ttype })
                    captured = []
                 
                captured.append(line)
                line_start = k
                capturing = True
            else:
                captured.append(line.strip())

            line = sourcef.readline()
            k = k + 1

        if captured:
            result.append({'line': line_start, 'content': "".join(k + ' ' for k in captured).strip(),
                'type': ttype })

    return result

# Entrypoint

parser = argparse.ArgumentParser()
parser.add_argument("-path", type=str, help="Path where this is installed.")
parser.add_argument("-output", type=str, help="Output format. Options: 'plain,concise'.", default="plain")
# Disabled until I can get the behaviour in vim to be correct, may not be
# neccessary.
parser.add_argument("-shorten", type=bool, help="True to shorten directorys on concise output", default=False)
args = parser.parse_args()

if args.shorten:
    args.shorten = False


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
    # Disregard any errors opening this file.
    pass

largest_number = 0
patterns_file  = "%spatterns" % args.path

with open(patterns_file, "r") as pfile:
    patterns = pfile.readlines()

patterns = [ p.strip() for p in patterns ]
comment_tokens = { 'py': '#', 'tex': '%', 'm': '%', 'wiki': '%%' }
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

    if ext == "py" or ext == 'tex' or ext == 'm' or ext == 'wiki':
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


if args.output == 'plain':
    if todo_count > 0:
        print 'Summary: %s item(s) to do.' % (todo_count)
        print ''
    else:
        print "You're all done!"


keys = finfo.keys()
keys.sort()

k = 0
for f in keys:
    if args.output == 'plain':
        print 'File: %s' % f

        for item in finfo[f]:
            k = k + 1
            print ('  %03d) \t%0' + str(places) + 'd: %s') % (k, int(item["line"]), item["content"])

        print ''

    if args.output == 'concise':
        for item in finfo[f]:
            
            content = item["content"]
            filename = f

            # TODO: This doesn't work, because vim quickfix doesn't open
            # the correct file; a revised strategy w.r.t. vim error format
            # will be required. Implement.
            
            if args.shorten:
                t = filename.split('/')
                t = [ k for k in t if k ]

                # Shorten, vim-style
                if len(t) > 1:
                    filename = "".join("/" + k[0] for k in t[0:len(t) - 1]) + "/" + t[-1]
            
            if not content:
                content = "(empty)"
                
            print '%s:%s:%s' % (filename, item["line"], content)

if anything_modified:
    pdata = [finfo, mtimes]
    with open("%slast.dat" % args.path, "wb") as p:
        pickle.dump(pdata, p)
