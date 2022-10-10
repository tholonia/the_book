#!/bin/python
import pprint
import re,os
from pprint import *
import PyPDF2
import MySQLdb as mdb
from nltk.corpus import stopwords
nltk_stop_words = set(stopwords.words('english'))
from stop_words import get_stop_words
import nltk
stop_words = set(get_stop_words('en'))
import toml
import hashlib
from operator import itemgetter
import fitz
cfg = toml.load("index.toml")

from colorama import init, Fore, Back
init()

def make_Index_by_Category(entries):
    print("Preparing index 1: By Book - with categories")
    out = open(r"Index-by-Category.html", "w")
    out.write(makedocstart("Index by Category"))
    for heading in entries:
        if entries[heading]:
            out.write("<span class='hbox'>")
            pr_heading(out, heading, chapter=1)
            out.write("<span class='lbox'>")
            for line in entries[heading]:
                pr_line(out, line)
            out.write("</span>")
            out.write("</span>")
    out.write(docend)
    out.close()

def make_Index(entries,**kwargs):
    print("Preparing index 1: By Book")

    colors = False
    try:
        colors = kwargs['colors']
    except:
        pass

    out = open(r"Index.html", "w")
    out.write(makedocstart("Index"))
    flat = []
    for heading in entries:
        for e in entries[heading]:
            flat.append(e)
    flat.sort(key=lambda x: x[0].lower())
    out.write("<span class='lbox'>")

    for line in flat:
        pr_line(out, line, colors=colors)
    out.write("</span>")
    out.write("</span>")
    out.write(docend)
    out.close()

# def make_xflc(entries,**kwargs):
#     colors = True
#
#     out = open(r"xflc.html", "w")
#     out.write(makedocstart("3: By Book - category colored words", colors=colors))
#     flat = []
#     for heading in entries:
#         for e in entries[heading]:
#             flat.append(e)
#     flat.sort(key=lambda x: x[0].lower())
#     out.write("<span class='lbox'>")
#
#     for line in flat:
#         pr_line(out, line, colors=colors)
#     out.write("</span>")
#     out.write("</span>")
#     out.write(docend)
#     out.close()
#
# def make_xcha(onlychap):
#     chnames = cfg["chapter_titles"]
#     out = open(r"xcha.html", "w")
#     out.write(makedocstart("4: By Chapter - catagories by chapters"))
#     # pr_desc(out, "BY CHAPTER")
#     from_chapter = 1
#     chapters = 7  # int(to_list(sqlex("select max(ch) from words"))[0])
#     # print(chapters)
#
#     # + override chapters
#     if onlychap:
#         from_chapter = onlychap
#         chapters = onlychap + 1
#
#     for i in range(from_chapter, chapters):
#         pr_chapter(out, f"Chapter {i}: {chnames[i]}")
#         entries = get_pages(i + 1)
#         # # + final output
#         for heading in entries:
#             if entries[heading]:
#                 out.write("<span class='hbox'>")
#                 pr_heading(out, heading, chapter=i)
#                 out.write("<span class='lbox'>")
#                 for line in entries[heading]:
#                     pr_line(out, line)
#                 out.write("</span>")
#                 out.write("</span>")
#     out.write(docend)
#     out.close()


def get_active_words():
    cmd = '''
            SELECT word FROM headings 
            WHERE 
                type = 'w' 
            ORDER BY ID DESC
    '''
    db_words = to_list(sqlex(cmd))
    return db_words

def rebuilddb():
    sqlex("SET autocommit=0;")
    sqlex("delete from pages")
    lines_ary, words_ary = loadpages(cfg['file'])
    for pagenum in range(len(words_ary)):
        for word in words_ary[pagenum]:
            cmd = f"INSERT IGNORE into pages (word,pagenum) VALUES ('{word}','{pagenum+1}')"
            # print(Fore.CYAN+cmd+Fore.RESET)
            sqlex(cmd)
    for pagenum in range(len(lines_ary)):
        cmd = f"INSERT IGNORE into pages (page,pagenum) VALUES ('{lines_ary[pagenum]}','{pagenum+1}')"
        # print(Fore.BLUE + cmd + Fore.RESET)
        sqlex(cmd)
    sqlex("SET autocommit=1;",commit=True)
def populate_by_phrase(db_words):
    # + get all active word
    cmd = '''
            SELECT word FROM headings 
            WHERE 
                type = 'p' OR type = 'n' 
            ORDER BY ID DESC
    '''
    db_words = to_list(sqlex(cmd))

    for findword in db_words:
        pages = []
        # + query on the wildcard
        cmd = f'''
            SELECT DISTINCT
                p.pagenum,
                p.page,
                h.display
            FROM
                pages AS p,
                headings AS h
            WHERE
                p.page LIKE '%{findword}%'
            AND h.type != 'w' 
            AND h.word = '{findword}'
            '''
        # print(Fore.YELLOW + cmd + Fore.RESET)
        pagelist = (sqlex(cmd, dict=True))
        if pagelist:
            pages = []
            for pageary in pagelist:
                pages.append(pageary['pagenum'])

            # + get heading and display
            cmd = f'''
                SELECT
                 headings.heading,
                 headings.display,
                 headings.word
                FROM
                 headings
                WHERE
                 headings.word LIKE '%{findword}%'
            '''
            # print(Fore.RED+cmd+Fore.RESET)
            # print(f"[{findword}],[{fmtgroup(pages)}])
            frs = sqlex(cmd)
            # print(frs)
            if frs:
                heading = frs[0][0]
                display = frs[0][1]
                word = frs[0][2]
                display = word if not display else display

                # print(f"[{findword}],[{fmtgroup(pages)}],[{heading}],[{display}],[{word}]")

                # # + add results to DB
                cmd = f'''
                    INSERT IGNORE into results (hash,heading,display,pages)
                    values ('{hashit(heading + word)}','{esc(heading)}','{esc(display)}','{fmtgroup(pages,string=True)}')
                '''
                sqlex(cmd)
def populate_by_word(db_words):
    for findword in db_words:
        comparg = "="
        if str(findword).find("%") != -1:
            comparg = "LIKE"
        # print(Fore.GREEN+comparg+Fore.RESET)
        wordtype = list(sqlex(f"select type from headings where word = '{findword}'", dict=True))[0]['type']

        pages = []
        # + query on the wildcard
        # if wordtype == 'w':
        cmd = f'''
            SELECT DISTINCT
                p.pagenum,
                h.display,
                p.word AS p_word,
                h.word AS h_word
            FROM
                pages AS p,
                headings AS h
            WHERE
                h.type = 'w'
            AND p.word LIKE h.word
            AND p.word {comparg} '{findword}'
            '''

        pagelist = (sqlex(cmd, dict=True))
        if pagelist:
            pages = []
            for pageary in pagelist:
                pages.append(pageary['pagenum'])

            # + get heading and display
            cmd = f'''
                SELECT
                 headings.heading,
                 headings.display,
                 headings.word
                FROM
                 headings
                WHERE
                 headings.word {comparg} '{findword}'
                AND disabled is NULL
            '''
            # print(Fore.RED+cmd+Fore.RESET)
            # print(f"[{findword}],[{fmtgroup(pages)}])
            frs = sqlex(cmd)
            # print(frs)
            if frs:
                heading = frs[0][0]
                display = frs[0][1]
                word = frs[0][2]
                display = word if not display else display

                # print(Fore.MAGENTA+f"[{findword}],[{fmtgroup(pages)}],[{heading}],[{display}],[{word}]"+Fore.RESET)
                # print(f"[{findword}]")

                # # + add results to DB
                cmd = f'''
                    INSERT IGNORE into results (hash,heading,display,pages)
                    values ('{hashit(heading + word)}','{heading}','{display}','{fmtgroup(pages,string=True)}')
                '''
                sqlex(cmd)

def merge_dups():
    cmd='''
        SELECT
            count(*)AS c,
            display
        FROM
            results
        GROUP BY
            display
	'''
    rs = sqlex(cmd)
    for r in rs:
        if r[0] >1:
            clist = []
            heading = ""
            display = ""
            dups = sqlex(f"SELECT * FROM results WHERE display='{r[1]}'",dict=True)
            for dup in dups:
                heading = dup['heading']
                display = dup['display']
                # print(dup)
                dentry = dup['pages'].split(',')
                clist +=  [int(x) for x in dentry]
                cmd = f"DELETE FROM results WHERE hash = '{dup['hash']}'"
                # print(Fore.RED+cmd+Fore.RESET)
                sqlex(cmd)
            clist =  [str(x) for x in clist]
            # pprint(clist)
            cmd = f"INSERT INTO results (hash,heading,display,pages) VALUES ('{hashit(heading + display)}','{heading}','{display}','{fmtgroup(clist,string=True)}')"
            # print(Fore.YELLOW+cmd+Fore.RESET)
            sqlex(cmd)

            # pprint(ts[0][3].split(','))
    # pprint(rs)
    # exit()

def reformpg():
    cmd = "SELECT * FROM results"
    rs = sqlex(cmd,dict=True)
    # print(rs)
    for r in rs:
        pgrp = fmtgroup(str(r['pages']).split(","))
        hash = r['hash']
        cmd = f"UPDATE results SET pages = '{pgrp}' WHERE hash = '{hash}'"
        sqlex(cmd)
        # print(Fore.YELLOW+cmd+Fore.RESET)
def cleanold():
    sqlex("delete from results")
    # try:
    #     os.unlink("xcha.html")
    # except:
    #     pass
    # try:
    #     os.unlink("xall.html")
    # except:
    #     pass
    # try:
    #     os.unlink("xfla.html")
    # except:
    #     pass
    # try:
    #     os.unlink("xflc.html")
    # except:
    #     pass

import shlex
# 100000 words -> https://www.mit.edu/~ecprice/wordlist.10000
# *******************************************************************

def makeintro(**kwargs):

    try:
        if kwargs['skip']:
            return " "
    except:
        pass


    colors = False
    try:
        colors = kwargs['colors']
    except:
        pass
    if not colors:
        intro = '''
        <div class="intro">
        <p>This index has been organized on the premise that: Everything is <strong>energy</strong>, and the movement of energy forms patterns, or <strong>archetypes</strong>, which <strong>instantiate</strong> as form.  By observing these forms, <strong>people</strong> create <strong>models</strong> to understand and implement <strong>order</strong>.</p>
        <ul>
            <li><strong>Archetypes</span></strong>; a perfect or ideal structure of an instance.</li>
            <li><strong>Energy</strong>; movement, heat, force, power, awareness, intention.</li>
            <li><strong>Instances</strong>; how archetypes are expressed in tour material reality.</li>
            <li><strong>Models</strong>; theories, beliefs, perspectives of understanding.</li>
            <li><strong>Order</strong>; patterns in chaos.</li>
            <li><strong>People</strong>; real or legendary folks that have contributed to our knowledge.</li>    
        </ul>
        </div>
            '''
    else:
        intro = '''
        <div class="intro">
        <p>This index has been organized on the premise that: Everything is <strong>energy</strong>, and the movement of energy forms patterns, or <strong>archetypes</strong>, which <strong>instantiate</strong> as form.  By observing these forms, <strong>people</strong> create <strong>models</strong> to understand and implement <strong>order</strong>.</p>
        <ul>
            <li><strong><span class='wArchetypes'>Archetypes</span></strong>; a perfect or ideal structure of an instance.</li>
            <li><strong><span class='wEnergy'>Energy</span></strong>; movement, heat, force, power, awareness, intention.</li>
            <li><strong><span class='wInstances'>Instances</span></strong>; how archetypes are expressed in tour material reality.</li>
            <li><strong><span class='wModels'>Models</span></strong>; theories, beliefs, perspectives of understanding.</li>
            <li><strong><span class='wOrder'>Order</span></strong>; patterns in chaos.</li>
            <li><strong><span class='wPeople'>People</span></strong>; real or legendary folks that have contributed to our knowledge.</li>    
        </ul>
        </div>
        '''

    return intro

def makedocstart(title,**kwargs):
    colors = False
    try:
        colors = kwargs['colors']
    except:
        pass

    docstart = '''

    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <title>''' + title + '''</title>

    <link rel="stylesheet" href="reset.css" type="text/css" media="screen" charset="utf-8" />

        <script src="Columnizer-jQuery-Plugin-1.6.0/src/jquery.js"></script>
        <script src="Columnizer-jQuery-Plugin-1.6.0/src/jquery.columnizer.js"></script>
        <!-- link rel="stylesheet" href="indexitems.css" type="text/css" -->
        <script>
            $(function(){
                var content_height = 652;	// the height of the content, discluding the header/footer
                var page = 1;				// the beginning page number to show in the footer
                function buildNewsletter(){
                    if($('#newsletterContent').contents().length > 0){
                    // when we need to add a new page, use a jq object for a template
                    // or use a long HTML string, whatever your preference
                        $page = $("#page_template").clone().addClass("page").css("display", "block");
                        // fun stuff, like adding page numbers to the footer
                        $page.find(".footer span").append(page);
                        $("body").append($page);
                        page++;

                        // here is the columnizer magic
                        $('#newsletterContent').columnize({
                            columns: 2,
                            target: ".page:last .content",
                            overflow: {
                                height: content_height,
                                id: "#newsletterContent",
                                doneFunc: function(){
                                    console.log("done with page");
                                    buildNewsletter();
                                }
                            }
                        });
                    }
                }
                setTimeout(buildNewsletter, 3000);
            });
            Window.print();
    </script>
    <style>
 .page{ width: 612px; height: 920px; border: 1px solid black; margin: 20px; position: relative; }
//.page{ width: 7in; height: 10in; border: 0px solid black; margin: 20px; position: relative; }
.page .content .column{ text-align:justify; font-size: 10pt; }
.page .content .column blockquote{ border-left: 2px solid #999999; background: #DEDEDE; padding: 10px; margin: 4px 20px; clear: both; }
.page .content .column img{ float: left; margin: 10px; }
.page .content .column p{ padding: 0 10px; margin: 10px 0; }
.page .content .column h1{ padding: 0 10px; }
.page .header{ text-align: center; font-size: 18pt; font-family: helvetica, arial; padding: 20px 0 0; }
.page .header hr, .page .footer hr{ width: 400px; }
.page .footer{ text-align: center; }
.page .footer span{ position: absolute; bottom: 10px; right: 10px; }
#page_template{ display: none; }

.enclosure {border:1px dashed black}

.intro {
    margin:22px;
    width:612px;
}

ol, ul {
    list-style: inside;
    margin: 10px;
    line-height: 16px;
}
.first {
    width: 45%;
    float: left;
    margin-left: 5%;
}

.last {
    width: 45%;
    float: left;
    /* background-color: burlywood; */
}

@page {
    size: auto;   /* auto is the initial value */
    margin: 0;  /* this affects the margin in the printer settings */
}


.desc {
  color: #000000;
  font-weight: 600;
}
.heading {
   color: #000000;
   font-weight: 600;
   font-size: 13pt;
   height: 15px;
   padding-top: 4px;
   margin-bottom: 6px;
   font-style:italic;
   margin-left: 12px;
   width: -webkit-fill-available;
   background-color: lightgrey;
   padding-bottom: 6px;
   padding-left: 7px;
   margin-left: 10px;
   margin-top: 6px;    
   border: 1px solid black;
}
.hc1 {background-color: aqua;} 
.hc2 {background-color: burlywood;}
.hc3 {background-color: thistle;}
.hc4 {background-color: darkkhaki;}
.hc5 {background-color: gold;}
.hc6 {background-color: hotpink;}
.hc7 {background-color: mediumaquamarine;}
.line {
  margin-left: 10px;
  padding-bottom: 2px;
  border-left: black;
  /* height: 14px; */
  border-left: 3px solid lightgray;
  display: flex;
}
.word {
  /* background-color: blue; */
  width:fit-content;
  float:left;
  /* background-color:red; */
  font-size: 10pt;
  margin-left: 6px;
  font-weight:600;
  white-space: nowrap;
}
.w {}
.wArchetypes    {color: #ff0000;}    
.wChaos         {color: #ff00d8;}
.wEnergy        {color: #b000ff;}    
.wModels        {color: #4500ff;}    
.wOrder         {color: #005cff;}    
.wPeople        {color: #007e85;}    
.wInstances     {color: #748500;}

    
.wordplus {
  /* background-color: blue; */
  width:fit-content;
  float:left;
  /* background-color:red; */
  font-size: 10pt;
  margin-left: 6px;
  font-weight:400;
  text-align:left
}

  /* color: black;
/* } */
.pages {
  /* background-color: green; */
  width: fit-content;
  /* background-color: green; */
      width: -webkit-fill-available;
  font-size: 8pt;
  margin-left: 12px;
  padding-top: 1px;
  line-height: 9pt;
  font-style: italic;
  text-align:end !important;
}
  /* color: #5b5b5b;
} */
.chapter {
  color: #000000;
  padding-top: 12px;
  margin-bottom: 3px;
  font-size: 18pt;
  text-align: end;
}



.lbox {
  margin-left: 0px;
  /* border:1px solid green; */
}
.hbox {
  /* border:1px solid red; */
  margin-left: 16px;
}

    </style>
    <body>'''+makeintro(skip=True,colors=colors)+'''




    <div id="page_template">\
        <div class='header'>''' + title + f'''<hr></div>  
        <div class='content'></div>  
        <!--div class='footer'><hr><span>Page: </span></div-->  
        <div class='footer'><hr><span></span></div>  
    </div> 
    <div id="newsletterContent">
    '''
    return docstart


docend = '''
</div>
<script>
function fix() {
    console.log("fixing")
    $(".first").css({"width": "45%"});
    $(".last").css({"width": "45%"});
}

$( document ).ready(function() {
    console.log("onload")
    setTimeout(fix,6000)
});
</script>
</body>
</html>
'''


def pr_heading(f, s, **kwargs):
    try:
        chapter = kwargs['chapter']
    except:
        chapter = False

    if chapter:
        f.write(f"<div class='heading hc{chapter}'>{s}</div>")


def pr_line(f, s, **kwargs):
    colors=False
    try:
        colors=kwargs['colors']
    except:
        pass

    w = s[0]
    p = s[1]
    clr=""
    if colors:
        cmd = f'''
            SELECT DISTINCT
                heading
            FROM
                headings
            WHERE
                display = '{esc(w)}' or word = '{esc(w)}'  
        '''
        qclr = sqlex(cmd)
        # print(qclr)
        clr = qclr[0][0] if qclr else ""
        # exit()
    w1 = f"<span class='word w{clr}'>{w}</span>"
    w2 = ""
    if str(w).find(";") != -1:
        el = str(w).split(";")
        w1 = f"<span class='word w{clr}'>{el[0]}</span>"
        w2 = f";<span class='wordplus'>{el[1]}</span>"
    f.write(f'''
            <div class='line'>
            {w1}{w2}
            <span class='pages'>{p}</span>
            </div>
            '''
            )


def pr_chapter(f, s):
    f.write(f"<div class='chapter'>{s}</div>")


def pr_desc(f, s):
    f.write(f"<span class='desc'>{s}</span>")





def getdbconn():
    host = "localhost"
    dictionary = False
    username = 'root'
    password = 'edcrfv314'
    global dbc
    global cursor
    global d_cursor
    # cursor = False
    # dbconn = False
    try:
        dbc = mdb.connect(user=username, passwd=password, host=host, db="tholonia")
        # if dictionary:
        d_cursor = dbc.cursor(mdb.cursors.DictCursor)
        # else:
        cursor = dbc.cursor()

    except Exception as e:
        estr = f"ERROR!! [{e}] Could not init DB"
        print(estr)
        exit()

    cursor.execute("SET autocommit=1;")

    # return dbconn, cursor
def sqlex(cmd,**kwargs):
    dictionary = False
    show = False
    commit = False
    try:
        dictionary = kwargs['dict']
    except:
        pass
    try:
        show = kwargs['show']
    except:
        pass
    try:
        commit = kwargs['commit']
    except:
        pass

    # if show:
    #     print(Fore.GREEN+f"{cmd}"+Fore.RESET)

    global dbc
    global cursor
    global d_cursor

    if dictionary:
        this_cursor = d_cursor
    else:
        this_cursor = cursor

    try:
        this_cursor.execute(cmd)
        if commit:
            dbc.commit()
        # rs = cursor.fetchall()
        rs = list(this_cursor.fetchall())
          # rs = g.cursor.fetchone()
        return (rs)
    except Exception as e:
        estr = f"ERROR!! [{e}] Could not execute query query: [{cmd}]."
        print(estr)

# do stuff with my_var

def ranges(i):
    import itertools
    for a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]
def fmt_range(nslist):

    # if type(nslist) == str:
    #     nslist = [nslist]
    # print("nslist",nslist)

    # input:  [1,2,3,4]   int or str
    newlist = []
    strx=""
    # print("nslist")
    # pprint(nslist)
    # print(len(nslist))
    # print(type(nslist))
    if len(nslist)>1:
        for ns in nslist:
            start = ns[0]
            end = ns[1]
            if start != end:
                strx = f"{start}-{end}"
            else:
                strx = f"{start}"
            newlist.append(strx)
        # print("nel: ",newlist)
        return newlist
    else:
        # print("1el: ",[f"{list(nslist[0])[0]}"])
        return [f"{list(nslist[0])[0]}"]

def to_list(_rs):
    rs = []
    for i in _rs:
        rs.append(i[0])
    return(rs)

def loadpages(xFile):
    words_ary = []
    lines_ary = []
    # pdfDoc = PyPDF2.PdfFileReader(open(xFile, "rb"))
    pdfDoc = fitz.open(xFile)
    i=0

    for page in pdfDoc:
        page_text = str(page.get_text()).replace("\n"," ")
        # print(page_text)
        # exit()
        tokens = nltk.word_tokenize(page_text)
        # pprint(tokens)
        # punctuations = []
        punctuations = ['(', ')', ';', ':', '[', ']', ',']
        # stop_words = stopwords.words('english')
        # keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
        keywords = [word for word in tokens if not word in punctuations]
        # content = content.replace('\n',' ')
        # content1 = content.encode('ascii', 'ignore').lower()
        words_ary.append(keywords)
        # lines_ary.append(' '.join(keywords))
        lines_ary.append(page_text)
        # print(content1)
    # long_fw = ' '.join(finalwords)
    # return(fw)
    # for i in lines_ary:
    #    print(i,"\n\n")
    # exit()
    return(lines_ary, words_ary)

def fmtgroup(strlist,**kwargs):
    asstring = False
    try:
        asstring = kwargs['string']
    except:
        pass

    newstr = ""
    if asstring:
        newstr = ','.join(set(strlist))
    else:
        newlist = []
        intlist = [int(x) for x in set(strlist)]
        byranges = ranges(sorted(intlist))
        for r in byranges:
            if r[0] == r[1]:
                newlist.append(f"{r[0]}")
            else:
                newlist.append(f"{r[0]}-{r[1]}")

        newstr = ', '.join(newlist)
    return newstr


def hashit(str):
    hashval = hashlib.md5(str.encode())
    hashstr = f"{hashval.hexdigest()}"
    return hashstr
def strfind(xString):

    xString = xString.lower()
    xFile = cfg['file']
    pdfDoc = PyPDF2.PdfFileReader(open(xFile, "rb"))
    xString = xString.lower()
    for i in range(0, pdfDoc.getNumPages()):
        content = ""
        content += pdfDoc.getPage(i).extractText() + " "
        content = content.replace('\n',' ')
        content1 = content.encode('ascii', 'ignore').lower()
        ResSearch = re.search(r'(.{10})('+xString+')(.{10})', content1.decode('utf-8'))
        if ResSearch is not None:
            # rs = f"{ResSearch.group(1)}[{R/esSearch.group(1)}]{ResSearch.group(2)}"
            rs = f"{ResSearch.group()}"
            print(f"{rs} [pg:{i+1}, ch:{get_chapter(i)}]")
def esc(w):
    # print(f"SRC [{w}]")
    w= str(w).replace("'","''")
    return(w)

def pagefmt(tot):
    # print(type(tot))
    tot = tot.lstrip(",")
    # print(type(tot),tot)
    totlist = tot.split(",")
    # print(type(totlist),totlist)
    totlisti = [int(x) for x in totlist]
    # print(type(totlisti),totlisti)
    totlist=sorted(set(totlisti))
    # print(type(totlist),totlist)

    # totlists = [str(x) for x in totlist]
    # tstr = ', '.join(totlists)
    f = sorted(list(ranges(totlisti)))
    # print(type(f),f)
    ftstr = fmt_range(f)
    # print(type(ftstr),ftstr)
    fout = ", ".join(ftstr)
    # print("---------------------")
    return(fout)

def get_pages(ch):

    # + get list of heading names
    cmd = f"select distinct heading from headings"
    q_headings = to_list(sqlex(cmd))
    entries = {}

    for h in q_headings:
        entries[h]=[]

    query_results = sqlex("select heading,display,pages from results order by display", dict=True)

    # pprint(query_results)
    for k in range(len(query_results)-1):
        r = query_results[k]
        entries[r['heading']].append([r['display'], r['pages']])
    return entries


def get_chapter(pg):
    ch_beg_pg = cfg['ch_beg_pg']

    for i in range(len(ch_beg_pg)-1):
        f = ch_beg_pg[i]
        t = ch_beg_pg[i+1]
        if pg >= f and pg < t:
            return(i+1)

    print(f">>>> No chapter found for page {pg}")
    return 0
def xxxpdffind(pages, xString):
    PageFound = []

    i=0
    for page in pages:
        # print(page)
        ResSearch = re.search(xString, str(page).lower())
        if ResSearch is not None:
           PageFound.append(i)
        i+=1
    # exit()
    return PageFound
def xxxclean_list(raw):
    # print(raw)
    # !removed \’

    raw = raw.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+↩”“–"})
    delims = " "
    # pdf_words =stop_words.difference(re.split(delims,raw))
    # pdf_words =nltk_stop_words.difference(pdf_words)
    #
    pdf_words = set(re.split(delims,raw)).difference(stop_words)
    pdf_words = list(pdf_words.difference(nltk_stop_words))

    for i in range(len(pdf_words)):
        # print(pdf_words[i])
        try:
            if pdf_words[i].isnumeric():
                # print(f"IS: {pdf_words[i]}")
                pdf_words[i]=''
                # print(f"NOW: {pdf_words[i]}")

            try:
                if len(pdf_words[i]) == 1:
                    try:
                        pdf_words[i]=''
                    except:
                        pass
            except:
                pass
        except:
            pass
    while ('' in pdf_words): pdf_words.remove('')


    return pdf_words
def xxxshowlist(col):
    cmd = f"select id,word,display,heading,disabled from headings order by `{col}`"
    rs = sqlex(cmd,dict=True)

    for r in rs:
        h = r['heading']
        w = r['word']
        v = "-d "+Fore.RED + f"'{r['display']}'" if r['display']  else ""

        strx = f"[{r['id']:03d}]  NI -h "+Fore.YELLOW + f"{h:12s}"+Fore.RESET+" -w "+ Fore.GREEN + f"'{w}' "+Fore.RESET+v+Fore.RESET
        print(strx)

    strx = f"[id]  NI -h "+Fore.YELLOW + f"heading"+Fore.RESET+" -w "+ Fore.GREEN + f"'word' "+Fore.RESET+" -d "+Fore.RED+"'display'"+Fore.RESET
    print("")
    print(strx)
