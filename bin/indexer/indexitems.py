#!/bin/python
import getopt
import sys
from indexitems_lib import *

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
repickle = False
argv = sys.argv[1:]
onlychap = False
rebuild = False
try:
    opts, args = getopt.getopt(argv, "-hc:r", ["help","--chapter=","rebuild="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        sys.exit(0)
    if opt in ("-c", "--chapter"):
        onlychap = int(arg)
    if opt in ("-r", "--rebuild"):
        rebuild=True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
getdbconn()
cleanold()
cfg = toml.load("index.toml")
file = cfg['file']
firstpage = cfg['firstpage']
lastpage = cfg['lastpage']

db_words =  get_active_words()# to_list(sqlex(cmd))

if rebuild: rebuilddb()

populate_by_word(db_words)
populate_by_phrase(db_words)
merge_dups()
# + now reformat the pages as groupings
reformpg()

entries = get_pages(False)

# pprint(entries)

# + final output
make_Index_by_Category(entries)
make_Index(entries)
# make_xflc(entries)
# make_xcha(onlychap)

print('''
Output files:
brave file:///home/jw/books/tholonia/bin/indexer/Index-by-Category.html
brave file:///home/jw/books/tholonia/bin/indexer/Index.html

Browser PDF margin setting:
----------------------------
top:    0.19"
bottom: 0.5"
left:   0.45"
right:  0.0"
''')
