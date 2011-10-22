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
#
# TODO:
#   - Only open files that have been modified since the
#       the last running of find-todo (use pickle).

import io
import sys
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
finfo = {}

largest_number = 0
todo_count     = 0

patterns_file = "%spatterns" % args.path

with open(patterns_file, "r") as pfile:
    patterns = pfile.readlines()

patterns = [ p.strip() for p in patterns ]

comment_tokens = { 'py': '#', 'tex': '%', 'm': '%' }

for raw_line in lines:
    splat       = raw_line.split(':')
    
    f           = splat[0]
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

        todo_count = todo_count + len(todos)

    for t in todos:
        if finfo.has_key(f):
            finfo[f].append(t)
        else:
            finfo[f] = [t]


places = 0
while largest_number > 0:
    largest_number = largest_number / 10
    places = places + 1


if todo_count > 0:
    print 'Summary: %s item(s) to do.' % (todo_count)
    print ''
else:
    print "You're all done!"


k = 0
for f in finfo:
    print 'File: %s' % f

    for item in finfo[f]:
        k = k + 1
        print ('  %03d) \t%0' + str(places) + 'd: %s') % (k, int(item["line"]), item["content"])

    print ''
