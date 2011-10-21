# Find's alll todo items in files sent to it by grep.
import sys

lines = sys.stdin.readlines()

finfo = {}

largest_number = 0

for raw_line in lines:
    splat       = raw_line.split(':')
    
    f           = splat[0]
    line_number = splat[1]
    content     = "".join(splat[2:])

    d = { 'line': line_number, 'content': content.strip() }

    largest_number = max(largest_number, int(line_number))

    if finfo.has_key(f):
        finfo[f].append(d)
    else:
        finfo[f] = [d]

    l = content.strip()


places = 0
while largest_number > 0:
    largest_number = largest_number / 10
    places = places + 1


for f in finfo:
    print 'File: %s' % f

    for item in finfo[f]:
        print ('\t%0' + str(places) + 'd: %s') % (int(item["line"]), item["content"])

    print ''

