#!/usr/sbin/python


import publish_lib as pl
import re
import os

os.chdir("/home/jw/books/tholonia/chapters/INDEXED/")
chapters = pl.chapters


idx = 1
for chapter in chapters:
    fname = f'{chapter}.md'
    # print("-------------------------------------------------")
    print(f"{fname}")
    # print("-------------------------------------------------")
    file = open(fname, mode='r')
    lines = file.readlines()
    file.close()
    for i in range(len(lines)):
        m = re.search(r'^(#### \*\*Key.).*(:.*)',lines[i].strip())
        if (m != None):
            newline = f"{m.group(1)}{idx}{m.group(2)}"
            lines[i] = newline+"\n"
            idx +=1
    file = open(fname, mode='w')
    file.writelines(lines)
    file.close()
