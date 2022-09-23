#!/bin/python
import getopt,sys
import os

from indexitems_lib import *
getdbconn()

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
argv = sys.argv[1:]

word="EMPTY"
header="EMPTY"
chapter = 0
display = ""
action = "update"
fstr = False

try:
    opts, args = getopt.getopt(argv, "kw:h:d:a:F:HRL:gc:S:X",
        ["keywords","word=","header=","display=","action=","find=","headings","rebuild","list=","gen=","chapter=","show=","reindex"])
except getopt.GetoptError as err:
    sys.exit(2)

if len(opts) == 0:
    print("\t")
    print(f"\t-w|--word <string>     (Add word)")
    print(f"\t-c|--chapter <string>  (chapter or word)")
    print(f"\t-h|--header <string>   (Choose heading)")
    print(f"\t-d|--display <string>  (Alt entry)")
    print(f"\t-a|--action <u|d>      (Update or Delete entry)")
    print(f"\t-F|--find <word>       (Seach for word in PDF file)")
    print(f"\t-S|--show <word>       (Seach for word in DB)")
    print(f"\t-L|--list <colname>    (Show list of entries, order by <colname>)")
    print("\t")
    print(f"\t-X|--reindex   (reindex entries")
    print(f"\t-k|--keywords   (List all keywords")
    print(f"\t-g|--gen        (generate input commands")
    print(f"\t-H|--headings   (List all heading)")
    print(f"\t-R|--rebuild    (Build index)")
    print("\t")
    print("\tExample:")
    print("\t\tNI -h People -w 'Isaac Newton' -d 'Newton, Isaac'      (add an entry)")
    print("\t\tNI -h People -w 'Isaac Newton' -d 'Newton, Isaac' -a d (delete an entry)")
    print("\t")

    sys.exit(0)

# print(opts)
# exit()
for opt, arg in opts:

    if opt in ("-X", "--reindex"):
        rs = sqlex("select * from headings",dict=True)
        idx = 1
        for r in rs:
            h=r['heading']
            w=r['word']
            c=r['chapter']
            d=r['display']
            rx = sqlex(f'''
                        UPDATE headings SET idx = {idx} WHERE 
                        heading = '{h}' AND 
                        chapter = '{c}' AND 
                        word ='{w}' AND 
                        display = '{d}'
                ''')
            idx += 1

            exit()
    if opt in ("-g", "--gen"):
        rs = sqlex("select * from headings",dict=True)
        for r in rs:
            h=f"--header \"{r['heading']}\""
            w=f"--word \"{r['word']}\""
            c=f"--chapter \"{r['chapter']}\"" if r['chapter'] else ""
            dd = str(r['display']).replace("'","''")
            d=f"--display \"{dd}\"" if dd else ""
            print(f'./indexitems_new.py {h} {w} {c} {d}')

        # pprint(rs)
        exit()
        for k in rs:
            print(Fore.YELLOW+k)
        print(Fore.RED+"========================")
        exit()

    if opt in ("-S", "--show"):
        word = arg
        print(Fore.RED+"========================")
        cmd=f"select * from headings where word like '%{word}%'"
        rs = sqlex(cmd, dict=True)
        if len(rs) != 0:
            for i in range(len(rs)):
                for key in rs[i]:
                    print(f"{key:20s} [{rs[i][key]}]")
                print(Fore.RED+"========================"+Fore.RESET)
        exit()
    if opt in ("-L", "--list"):
        showlist(arg)
        exit()

    if opt in ("-h", "--header"):
        header = arg.lower().capitalize()

    if opt in ("-F", "--find"):
        fstr = arg
        strfind(fstr)
        exit()

    if opt in ("-H", "--headings"):
        for h in to_list(sqlex("select distinct heading from headings ORDER BY headings.heading ASC")):
            print(h)
        exit()
        display = arg

    if opt in ("-R", "--rebuild"):
        cmd = "rm x.md && ./indexitems.py > x.md && typora x.md &"
        print(cmd)
        os.system(cmd)
        exit()

    if opt in ("-d", "--display"):
        display = arg

    if opt in ("-a", "--action"):
        if arg == 'd':
            action = "delete"

    if opt in ("-w", "--word"):
        # word = arg.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+↩”“–"})
        word = arg

    if opt in ("-c", "--chapter"):
        # word = arg.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+↩”“–"})
        chapter = arg

# + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
# nltk_stop_words = set(stopwords.words('english'))
# stop_words = set(get_stop_words('en'))

#file = "/home/jw/books/tholonia/Latest/THOLONIA_THE_BOOK.pdf"
# file = "/home/jw/books/tholonia/chapters/TEST.pdf"

# firstpage = 5
# lastpage = 66

swtype = ""
wtype = "type = NULL"
if word.find(" ") != -1:
    wtype = "type = 'p'"
    swtype = "p"
if header.lower() == "people":
    wtype = "type = 'n'"
    swtype = "n"




if action == "update":
    #! first check for existing
    cmd = f"SELECT id,word,chapter,heading,display,type from headings WHERE word = '{word}'"
    rs = sqlex(cmd, dict=True)
    if len(rs)!=0:
        print(f"{Fore.RED}Word [{word}] already exists!!")
        for i in range(len(rs)):
            for key in rs[i]:
                print(f"{Fore.YELLOW}{key:20s} [{rs[i][key]}]")
            print("============================")
        print(Fore.RESET)
        x = input(f"{Fore.GREEN}x to quit, Enter to continue...")
        if x == "x":
            print("...exiting")
            exit()
    print(Fore.RESET)
    #! continuing


    cmd = f'''  INSERT INTO headings 
                (id,word,chapter,heading,display,type) VALUES (0,'{word}',{chapter},'{header}','{display}', '{swtype}') 
                ON DUPLICATE KEY 
                UPDATE word = '{word}', chapter = '{chapter}', heading='{header}', display='{display}', {wtype}
    '''
    sqlex(cmd)

    cmd = f''' SELECT id,word,chapter,heading,display,type from headings
    WHERE  
    word = '{word}' 
    '''
    rs = sqlex(cmd, dict=True)
    for i in range(len(rs)):
        for key in rs[i]:
            print(f"{key:20s} [{rs[i][key]}]")

if action == "delete":
    sqlex(f"delete from headings where word = '{word}' and heading = '{header}'")

    print(f"DELETED: [{header}]: [{word}]")
