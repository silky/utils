# Sample contents:
#
# <?xml version="1.0" encoding="utf-8"?>
# <!DOCTYPE documentInfo>
# <documentInfo url="/host/development/research/trunk/reference library/Verstraete2008, 4612Dd01.pdf">
#  <pageList>
#   <page number="5">
#    <annotationList>
#     <annotation type="4">
#      <base creationDate="2012-01-07T14:03:42" uniqueName="okular-5-1" author="Noon" modifyDate="2012-01-07T14:03:42" color="#ffff00">
#       <boundary l="0.218306" r="0.780116" b="0.218293" t="0.19065"/>
#      </base>
#      <hl>
#       <quad dx="0.533529" cx="0.780198" dy="0.190868" bx="0.780198" cy="0.190868" ax="0.533529" by="0.203447" ay="0.203447" feather="1"/>
#       <quad dx="0.218627" cx="0.6579" dy="0.20602" bx="0.6579" cy="0.20602" ax="0.218627" by="0.218599" ay="0.218599" feather="1"/>
#      </hl>
#     </annotation>
#    </annotationList>
#   </page>
#  </pageList>
#  </generalInfo>
# </documentInfo>

import os, glob, ConfigParser
from elementtree.ElementTree import parse
from pybtex.database.input import bibtex

def consider_file (t): # {{{
    try:
        data = parse(t)
    except Exception as moot:
        return

    pages = data.findall('pageList/page')

    if not pages or len(pages) <= 0:
        return

    t = os.path.basename(t).split('.')
    pdf = '.'.join(t[1:len(t) - 1])

    print ''
    print 'In %s we found: %s notes' % (pdf, len(pages))
    print 'hmm: %s%s' % (pdf_location, pdf)

    print dict_by_file[pdf+ ':' + pdf + ':PDF']

    for p in pages:
        annotations = p.findall('annotationList/annotation/base')
        page_number = int(p.get('number')) + 1

        print '\tOn page %s we have %s annotation(s).' % (page_number, len(annotations))

        for an in annotations:
            contents = an.get('contents')
            if contents:
                print '\t\t', contents
    # print content
# }}}


config = ConfigParser.ConfigParser()
config.read('main.conf')

okular_dir   = config.get('general', 'okular_dir')
bibtex_file  = config.get('general', 'bibtex_location')
pdf_location = config.get('general', 'pdf_location')


if __name__ == "__main__":

    parser = bibtex.Parser()
    bib = parser.parse_file(bibtex_file)
    items = bib.entries.items()
    dict_by_file = { k[1].fields['file']: k[1] for k in items if k[1].fields.has_key('file') }
    # print dict_by_file.keys()

    for f in glob.glob(os.path.join(okular_dir, '*.xml')):
        consider_file(f)

