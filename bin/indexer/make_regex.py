#!/bin/python
import sys
sys.path.append("/home/jw/books/tholonia/bin.indexer")
import regex as re
import getopt
from indexitems_lib import *
import glob
import toml
import subprocess
import codecs
from colorama import init, Fore, Back
init()

cfg = toml.load("/home/jw/books/tholonia/bin/indexer/index.toml")
skip = [
    ']:',
    'Synopsys',
    'keywords',
    '<img src',
    '<div',
    '<https:',
    'titlepage:',
    'subtitle:',
    'pubdate:',
    'title:',
    'author:',
    'ISBN-13:',
    'rights:',
    'rights-desc:',
    'status:',
    'publisher:',
    'toc:',
    'toc-title:',
    'version:',
    'lang:',
    'coverpage:',
    'subject:',
]
flags = re.IGNORECASE | re.MULTILINE
tagged_words = []
db_words=[]
def help():
    print("\t")
    print(f"\t-u|--update  (update live files with unindexed versions")
    print(f"\t-m|--mark  (add <u> and </u>")
    print(f"\t-c|--clean  (remove <u> and </u>")
    print(f"\t-h|--help")
    print("\t")

def override(word, contents):
    for i in range(len(contents)):
        contents[i].replace(word, codecs.encode(word, 'rot_13'))
    return(contents)

def mark(wordary, file_path):
    global tagged_words
    global db_words
    global skip
    global flags
    # ! --------------    DEBUG OPTION
    # wordary = ["volt%", "austria", "earth", "energy", "bohr"]

    file = open(file_path, "r")
    file_contents = file.read().split("\n")
    file.close()

    for word in wordary:
        pre_brackets = "[\s|\‘|\’|\“|\”|\"|\'|\?|\!|\*]{1}"
        suf_brackets = "[\s|\‘|\’|\“|\”|\"|\'|\?|\!|\)|\,|\[|\*]{1}"

        if word.find("%") != -1:
            word=word.replace("%","[a-zA-Z]*?")

        text_pattern1 = rf"({pre_brackets})({word})({suf_brackets})"
        text_pattern_BOL = rf"^({word})({suf_brackets})"
        text_pattern_EOL = rf"({pre_brackets})({word})$"

        for i in range(len(file_contents)):
            if any(e in file_contents[i] for e in skip):
                pass
            else:
                file_contents[i] = re.sub(text_pattern1, r"\1<u>\2</u>\3", file_contents[i], flags=flags)
                file_contents[i] = re.sub(text_pattern_BOL, r"<u>\1</u>\2", file_contents[i], flags=flags)
                file_contents[i] = re.sub(text_pattern_EOL, r"\1<u>\2</u>", file_contents[i], flags=flags)

    new_contents = "\n".join(file_contents)
    file = open(file_path, "w")
    file.write(new_contents)
    file.close()




def listw(file, aw):
    global srcdir
    file_path = f"{srcdir}/{file}"
    text_pattern = rf"<u>(.*?)</u>"
    flags = re.I | re.M | re.S
    file = open(file_path, "r")
    file_contents = file.read()
    file.close()
    groups = re.findall(text_pattern, file_contents, flags)

    for group in groups:
        aw.append(group)
    aw = set(aw)
    aw = sorted(aw)
    return(aw)

    # if len(groups):
    #     pprint(groups)

# def removetags(file_path, **kwargs):

def rebuild():
    rs = sqlex("select * from headings where disabled IS NULL", dict=True)
    for r in rs:
        print(f"`ins --header People --word 'Zhuang Zhou' --chapter 3 --display 'Zhou, Zhuang; philosopher'`")
        word = r['word']
        type = r['type']

def removetags():
    cmd="/home/jw/books/tholonia/bin/indexer/UNTAG"
    p = subprocess.Popen([cmd])
    p.wait()

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]

clean=False
markup=False
update=False
listwords=False

srcdir = "/home/jw/books/tholonia/chapters/INDEXED"
dstdir = "/home/jw/books/tholonia/chapters"
try:
    opts, args = getopt.getopt(argv, "hcmulr",
        ["help","clean","mark","update","list","rebuild"])
except getopt.GetoptError as err:
    sys.exit(2)
if len(opts) == 0:
    help()
    exit()

def waitfor(cmd):
    clist = str(cmd).split(" ")
    p = subprocess.Popen(clist)
    p.wait()
    return
for opt, arg in opts:
    if opt in ("-h", "--help"):
        help()
    if opt in ("-c", "--clean"):
        clean = True
    if opt in ("-u", "--update"):
        update = True
    if opt in ("-l", "--list"):
        listwords = True
    if opt in ("-r", "--rebuild"):
        rebuild()
    if opt in ("-m", "--mark"):
        try:
            os.chmod("/home/jw/books/tholonia/chapters/INDEXED/idxIndex-by-Category.md",0o666)
            os.chmod("/home/jw/books/tholonia/chapters/INDEXED/idxIndex.md",0o666)
        except:
            pass
        # waitfor("chmod a+rw /home/jw/books/tholonia/chapters/INDEXED/*")
        # exit()
        cmd="cp /home/jw/books/tholonia/chapters/*.md /home/jw/books/tholonia/chapters/INDEXED/"
        # print(cmd)
        # exit()
        os.system(cmd)
        markup = True

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

getdbconn()



if clean:
    print("Removing '<u>', '</u>'")
if markup:
    print("Adding '<u>', '</u>'")

# ! --------------    DEBUG OPTION
# files = cfg['chapter_meta_test']
files = cfg['chapter_meta']

allwords = []

# ! LOWER
# rs = sqlex("select id, LOWER(word) as word,type,chapter,edit,display,heading,disabled,wildcard  from headings where disabled IS NULL", dict=True)
rs = sqlex("select id, word,type,chapter,edit,display,heading,disabled,wildcard  from headings where disabled IS NULL", dict=True)
wordary = []
for r in rs:
    wordary.append(r['word'])


# - main routines
for mfile in files:
    file = mfile[2]

    file_path = f"{srcdir}/{file}"
    w = r['word']

    if clean:
        print(Fore.GREEN + f"Processing: [{file}]" + Fore.RESET)
        removetags(file_path)
    # if update:
    #     removetags(file_path, update=True)
    if markup:
        print(Fore.GREEN + f"Processing: [{file}]" + Fore.RESET)
        mark(wordary, file_path)
    if listwords:
        allwords = listw(file, allwords)

if update:
    removetags()

if listwords:
    sqlex("delete from stem")

    # - fill DB first
    for mfile in files:
        file = mfile[2]
        file_path = f"{srcdir}/{file}"

        file = open(file_path, "r")
        file_contents = file.read()
        file.close()


        # - get tagged words
        groups = re.findall("<u>(.*?)</u>", file_contents, flags=flags)
        # print(groups)
        if len(groups)>0:
            for k in groups:
                tagged_words.append(str(k).lower())
        tagged_words = sorted(list(set(tagged_words)))
        for f in tagged_words:
            cmd = f"insert ignore into stem(word) values('{f}')"
            sqlex(cmd)
        # for t in tagged_words:
        #     print(t)
        # exit()

    for mfile in files:
        file = mfile[2]
        print(Fore.CYAN + f"Reading: [{file}]" + Fore.RESET)
        file_path = f"{srcdir}/{file}"

        # - get expanded words
        expary = []
        for stemword in wordary:
            cmd = f"select s.word as expwords from stem as s, headings as h where s.word like h.word"
            rs5 = sqlex(cmd, dict=True)
            for x in rs5:
                expary.append(str(x['expwords']).lower())
        expary = sorted(list(set(expary)))
        # print(expary)

    difs = list(set(tagged_words) - set(expary))
    # print(Fore.RED,expary)
    # print(Fore.BLUE,tagged_words)
    print(Fore.MAGENTA)

    for d in difs:
        print(f"ins --header NA --word '{d}'")
    print(Fore.RESET)


'''
    for w in allwords:
        rs = sqlex(f"select count(*) as ct from headings where word like '{w}%' AND disabled IS NULL", dict=True)
        count = int(rs[0]['ct'])
        if count > 0:
            pass
            print(f"FOUND: [{w}]")

    testwords = []
    badwords = []
    for w in allwords:
        # ! LOWER
        # w = str(w).lower()
        rs = sqlex(f"select count(*) as ct from headings where word like '{w}%' AND disabled IS NULL", dict=True)
        count = int(rs[0]['ct'])
        if count <1:
            testwords.append(w)
            # print(w,)
            # cms = f"ins --header NA --word '{w}'"
            # print(cms)
    # ! LOWER
    # rs = sqlex(f"select LOWER(word) as word from headings where wildcard = 1 AND disabled IS NULL", dict=True)
    rs = sqlex(f"select word from headings where wildcard = 1 AND disabled IS NULL", dict=True)
    for wds in rs:
        dbword = wds['word']
        for tw in testwords:
            # ! LOWER
            # tw = str(tw).lower()
            stem = dbword[:-1]
            # print(f"[{stem}]   [{tw}]  ")
            if str(tw).find(stem) != -1:
                # print(f">>>>>{tw}")
                badwords.append(tw)

    # pprint(testwords)
    # pprint(badwords)
    res = [i for i in testwords if i not in list(set(badwords))]
    for r in res:
        cms = f"ins --header NA --word '{r}'"
        print(cms)
'''

