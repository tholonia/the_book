#!/bin/python
import os,sys, glob, subprocess, shutil
from pprint import *


# os.chdir("/home/jw/books/tholonia/bin/indexer")
# cmd="./indexitems.py"
# p=subprocess.Popen(cmd.split(" "))
# p.wait()
#
# exit()

os.chdir("/home/jw/books/tholonia/bin/indexer/pdf")


for file in glob.glob("*.png"):
    os.unlink(file)
for file in glob.glob("*~"):
    os.unlink(file)
try:
    shutil.move("Index by Category.pdf","Index-by-Category.pdf")
except:
    pass
for i in ["Index","Index-by-Category"]:
    print("\tMaking PNG")
    # pdffilename = f"{i}.pdf"

    cmd=f"/usr/bin/pdftoppm {i}.pdf -png {i}.pdf -png"
    # cmd=f"/usr/bin/pdftoppm {i} -png {pdffilename} -png"
    p=subprocess.Popen(cmd.split(" "))
    p.wait()

    print("\tCropping PNG")
    cmd = f"/usr/bin/mogrify -trim {i}*.png"
    p=subprocess.Popen(cmd.split(" "))
    p.wait()

    print("\tMaking MD")
    idx = open(rf"{i}.md","w")
    files = glob.glob(f"{i}*.png")
    files = sorted(files)
    # pprint(files)
    for file in files:
        shutil.copy(f"/home/jw/books/tholonia/bin/indexer/pdf/{file}", "/home/jw/books/tholonia/Images/index")
        idx.write(f"<img src='../Images/index/{file}' style='width:100%'>\n")
        idx.write("<div style='page-break-after: always; break-after: always;'></div>\n")
    idx.close()
    # print("XXX")
    frof=f"/home/jw/books/tholonia/bin/indexer/pdf/{i}.md"
    tof = f"/home/jw/books/tholonia/chapters/{i}.md"
    # print(frof)
    # print(tof)
    shutil.copy(frof,tof)
    # print("CCC")

    print(f"typora file:///home/jw/books/tholonia/chapters/{i}.md")