#!/bin/python
import getopt
import pickle
import sys,os
import subprocess
import operator

import toml
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from stop_words import get_stop_words

from indexitems_lib import *

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
chapter = "030-ORDER.py"
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hc:", ["help", "chapter="])
except getopt.GetoptError as err:
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h --help")
        print(f"-c  --chapter")
        sys.exit(0)

    if opt in ("-c", "--chapter"):
        chapter = arg
# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

file = open("_tmp", "r")
data = file.read()
data_list = data.split("\n")
fdata_list=[]
for x in data_list:
    if len(x) > 5:
        fdata_list.append(x)

twords = len(fdata_list)
vlimit = 1
limit = 1/200

w = False
wcAry = {}
for word in fdata_list:
    wc = fdata_list.count(word.strip())
    if wc > twords * limit:
        wcAry[word]=wc
# wcAry = {k: v for k, v in sorted(wcAry.items(), key=lambda item: item[0])}

x = sorted(wcAry.items(), key=lambda item: item[1], reverse=True)

print(f"{vlimit}% of {twords} = {twords * limit}")
only_words = []
for w in x:
    print(f"{w[0]:20s} {w[1]}")
    only_words.append(w[0])
print("")
print(', '.join(only_words))
