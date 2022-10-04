#!/usr/sbin/python

'''
the CSS files to edit are

../Styles/common_book_dev.css.less
../Styles/common_book_prod.css.less xxx
'''

import publish_lib as pl
import os
import sys
import getopt
import datetime
from colorama import init, Fore, Back
init()

now = datetime.datetime.now()
timestamp = now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))
pagesize = "7in 10in"
count = 0
H = "/home/jw/books/tholonia"
HOME = "/home/jw"
L = "Latest"
lb = "{"
rb = "}"
bs = "\\"


def report(s):
    print(Fore.RED+f"██████████████████████████████████████████████████████████████████ [{s}]"+Fore.YELLOW)
def status(s):
    print(Fore.GREEN+f"██████████████████████████████████████████████████████████████████ [{s}]"+Fore.YELLOW)
def get_version():
    report("get_version()")
    with open(f"{H}/inc/version.txt") as f:
        rs = f.readline().strip()
    f.close()
    return rs


def update_ver():
    report("update_ver()")
    vernum_before = get_version()
    os.system(f"{H}/bin/UPDATE_VERDATE.sh")
    vernum_after = get_version()
    # also update the titlepage image
    cx = f'''
        convert \
        -pointsize 80 \
        -font Times-Bold \
        -gravity South \
        -fill grey \
        -draw 'text 0,460 "Version {vernum_after}" ' \
        {H}/Images/titlepagev.png \
        {H}/Images/titlepage.png
    '''

    os.system(cx)
    return [vernum_before, vernum_after]


# ----------------------------------------------------------------------------------

def mkcss():
    report("mkcss()")
    os.system(f"rm {H}/Styles/common_book_*.css")
    os.system(f"rm {H}/Styles/epub_*.css")

    # first cpmpile the css to make
    # common_book_prod.css AND common_book_prod_header.css
    # OR
    # common_book_dev.css AND common_book_dev_header.css
    # make the css wrapped in <style> tag
    os.system(f"lessc {H}/Styles/common_book{STATE}.css.less {H}/Styles/common_book{STATE}.css")

    fname = f"{H}/Styles/common_book{STATE}.css"
    file = open(fname, mode='r')
    chap = file.read()
    mdall = f"<style>\n{chap}\n</style>\n"
    file.close()
    file = open(f"{H}/Styles/common_book{STATE}_header.css", mode='w')
    file.write(mdall)
    file.close()

    # then make the special epub css

    cxs = "lessc"

    cxs += f" --modify-var='h6-padding-bottom=5px'"
    cxs += f" --modify-var='list-margin-left=0%'"

    # tweak epub CSS so it works for footnote - epubs really so suck so much !

    # @footnote-ref-vertical-align: super;
    # @footnote-ref-font-size: smaller;
    # @footnote-ref-text-decoration: underline;
    # @footnote-ref-font-style: italic;
    # @footnote-ref-font-weight: bold;
    # @footnote-ref-margin-left: 2px !important;

    cxs += f" --modify-var='footnote-ref-vertical-align=super'"
    cxs += f" --modify-var='footnote-ref-font-size=smaller'"
    cxs += f" --modify-var='footnote-ref-text-decoration=underline'"
    cxs += f" --modify-var='footnote-ref-font-style=italic'"
    cxs += f" --modify-var='footnote-ref-font-weight-bold'"
    cxs += f" --modify-var='footnote-ref-margin-left=2px !important'"

    cxs += f" {H}/Styles/common_book{STATE}.css.less"
    cxs += f" {H}/Styles/epub{STATE}.css"

    os.system(cxs)

    fname = f"{H}/Styles/epub{STATE}.css"
    file = open(fname, mode='r')
    chap = file.read()
    mdall = f"<style>\n{chap}\n</style>\n"
    file.close()
    file = open(f"{H}/Styles/epub{STATE}_header.css", mode='w')
    file.write(mdall)
    file.close()


def rebuildmd(testname=""):
    report("rebuildmd(testname='')")
    mdall = ""
    idx = 0
    chapters = pl.chapters
    if testname:
        chapters = [testname]

    for chapter in chapters:
        if (idx >= pl.limit_fr) and (idx <= pl.limit_to):
            # if idx < pl.limit:
            # print(f"Reading chapter {chapter}.md")
            fname = f'{H}/chapters/{chapter}.md'
            print(f"\t{idx}  {fname}")
            file = open(fname, mode='r')
            chap = file.read()
            mdall += chap
            mdall += "\n\n"  # "<div style='page-break-after: never; break-after: none;'></div>\n"
            file.close()
        idx += 1
    file = open(f"{H}/chapters/THOLONIA_THE_BOOK.md", mode='w')
    file.write(mdall)
    file.close()
    print(f"Complete file: {H}/chapters/THOLONIA_THE_BOOK.md")


def html2pdf(chapter):
    report(f"chapter({chapter})")
    vernum = get_version()
    cx = "prince-books"
    cx += f" --pdf-title='THOLONIA v.{vernum}'"
    cx += f" --pdf-title='THOLONIA v.{vernum}'"
    cx += f" --pdf-subject='The Mechanics of Existential Awareness'"
    cx += f" --pdf-author='Duncan Stroud'"
    cx += f" --pdf-keywords='philosophy esoteric history mythology iching science'"
    cx += f" --pdf-creator='Typora Markdown, Pandoc, PrinceXML'"
    cx += f" --style={H}/Styles/common_book{STATE}.css"
    # cx += f" --style={H}/Styles/PRINCE-HTML-PDF.css"
    cx += f" --media=print"
    cx += f" --page-size='{pagesize}'"
    cx += f" -i html5"
    cx += f" -o {H}/chapters/{chapter}.pdf"
    cx += f" {H}/chapters/__temp.html"
    status(f"EXECUTING html->pdf:  {cx}")
    os.system(cx)


def md2html(chapter):
    report(f"md2html({chapter})")
    vernum = get_version()
    cx = "pandoc"
    cx += f" --pdf-engine=xelatex"
    cx += f" --include-in-header=file:///home/jw/books/tholonia/Styles/common_book{STATE}_header.css"
    cx += f" --from=markdown+tex_math_dollars+tex_math_single_backslash"
    cx += f" --template=tholonia.html5"  # /usr/share/pandoc/data/templates/
    cx += f" --to=html5"
    cx += f" --metadata-file={H}/inc/metadata.yaml"
    cx += f" --standalone"
    cx += f" --mathjax"
    cx += f" --verbose"
    cx += f" --top-level-division=chapter"
    # cx += f" --lua-filter={H}/inc/pagebreak.lua" #using HTML instead
    cx += f" --toc"
    cx += f" --webtex"  # current;y using local images so not nec
    cx += f" --metadata title='Tholonia'"
    cx += f" -o {H}/chapters/__temp.html"
    cx += f" {H}/chapters/{chapter}.md"

    status(f"EXECUTING html->html:  {cx}")
    os.system(cx)


def md2epub(chapter):
    report(f"md2epub({chapter})")
    vernum = get_version()
    cx = "pandoc"
    cx += f" --include-in-header=file:///home/jw/books/tholonia/Styles/epub{STATE}_header.css"
    cx += f" --css={H}/Styles/epub{STATE}.css"
    cx += f" --from=markdown+yaml_metadata_block+tex_math_dollars+tex_math_single_backslash"
    cx += f" --template={H}/Styles/tholonia.epub3"  # /usr/share/pandoc/data/templates/
    cx += f" --to=epub3"
    cx += f" --epub-cover={H}/Images/publish/epub/i6.69x9.61_Front-Only.jpg"
    cx += f" --standalone"
    cx += f" --mathjax"
    # cx += f" --self-contained"
    cx += f" --embed-resources --standalone"
    cx += f" --verbose"
    cx += f" --metadata title='THOLONIA:The Book'"
    cx += f" --top-level-division=chapter"
    cx += f" --toc"
    cx += f" --toc-depth=2"
    cx += f" -o {H}/chapters/{chapter}.epub"
    cx += f" {H}/chapters/{chapter}.md"

    status(f"EXECUTING md->epub:  {cx}")
    os.system(cx)


def convert_all():
    report("convert_all()")
    # manualy export each chapter to HTML in Typora

    idx = 0
    for chapter in pl.chapters:
        if (idx >= pl.limit_fr) and (idx <= pl.limit_to):
            # print("\n!!!!!!!")
            print(f"PROCESSING {chapter} (idx={idx})")
            # print("!!!!!!!\n")
            # export to HTML v1
            md2html(chapter)

            # export to HTML v2
            html2pdf(chapter)
        idx += 1

    # print("\n!!!!!!!")
    # print(f"FINISHING...")
    # print("!!!!!!!\n")


def pub_prep():
    report("pub_prep()")

    # print("PUBLISHING PREP\n-----------------------------------------\n")
    cx = f'''\
    rm -rf {HOME}/tmp >{H}/log 2>&1 #empty tmp dir used to make zip
    rm  {H}/{L}/*   #remove all in Latest
'''
    #    find {H}/{L} -type l -exec rm {lb}{rb} {bs};  #remove all linked versions

    print(cx)
    res = os.system(cx)
    print(f"return={res}")



def pub_pdf():
    report("pub_pdf()")
    vernum = get_version()
    #    {H}/bin/DELIMG.sh {H}/chapters/THOLONIA_THE_BOOK.pdf
    # print("PUBLISHING PDF\n-----------------------------------------\n")
    cx = f'''\
    cp {H}/chapters/THOLONIA_THE_BOOK.pdf {H}/Latest
    cp {H}/{L}/THOLONIA_THE_BOOK.pdf {H}/{L}/THOLONIA_THE_BOOK_v{vernum}.pdf
    '''
    print(cx)
    res = os.system(cx)
    print(f"return={res}")



def pub_epub():
    report("pub_epub()")
    vernum = get_version()
    # print("PUBLISHING EPUB\n-----------------------------------------\n")
    cx = f'''\
    cp {H}/chapters/THOLONIA_THE_BOOK.epub {H}/Latest
    cp {H}/{L}/THOLONIA_THE_BOOK.epub {H}/{L}/THOLONIA_THE_BOOK_v{vernum}.epub
    '''
    print(cx)
    res = os.system(cx)
    print(f"return={res}")


def pub_md():
    report("pub_md()")
    vernum = get_version()
    # print("PUBLISHING MD\n-----------------------------------------\n")
    cx = f'''\
    cp {H}/chapters/THOLONIA_THE_BOOK.md {H}/Latest
    cp {H}/{L}/THOLONIA_THE_BOOK.md {H}/{L}/THOLONIA_THE_BOOK_v{vernum}.md
    '''
    print(cx)
    res = os.system(cx)
    print(f"return={res}")



def pub_html():
    report("pub_html()")
    # print("PUBLISHING HTML\n-----------------------------------------\n")
    vernum = get_version()
    cx = f'''\
    cp {H}/chapters/__temp.html {H}/Latest/THOLONIA_THE_BOOK.html
    mv {H}/chapters/__temp.html {H}/chapters/THOLONIA_THE_BOOK.html
    cp {H}/{L}/THOLONIA_THE_BOOK.html {H}/{L}/THOLONIA_THE_BOOK_v{vernum}.html
    '''
    print(cx)
    res = os.system(cx)
    print(f"return={res}")



def pub_zip():
    report("pub_zip()")
    # print("MAKE/PUBLISHING ZIP\n-----------------------------------------\n")
    vernum = get_version()
    cx = f'''\

    rm -rf {HOME}/tmp
    mkdir -p {HOME}/tmp/Images
    cp {H}/{L}/THOLONIA_THE_BOOK.html {HOME}/tmp
    cp {H}/Images/*.png {HOME}/tmp/Images
    cd {HOME}/tmp
    perl -pi -e 's/...Images/Images/gmi' {HOME}/tmp/THOLONIA_THE_BOOK.html
    zip --quiet -r THOLONIA_THE_BOOK.html.zip *
    cp {HOME}/tmp/THOLONIA_THE_BOOK.html.zip {H}/{L}
    cd {H}

    cp {H}/{L}/THOLONIA_THE_BOOK.html.zip {H}/{L}/THOLONIA_THE_BOOK_v{vernum}.html.zip
    '''
    print(cx)
    res = os.system(cx)
    print(f"return={res}")



def mkdocs(testname=""):
    report("mkdocs(testname='')")

    rebuildmd(testname)  # make new complete MD file
    md2html("THOLONIA_THE_BOOK")
    html2pdf("THOLONIA_THE_BOOK")
    md2epub("THOLONIA_THE_BOOK")


def mkpub():
    report("mkpub()")
    mkdocs()
    pub_prep()
    pub_epub()
    pub_pdf()
    pub_md()
    pub_html()
    pub_zip()


def cleanold():
    report("cleanold()")
    os.system(f"rm {H}/chapters/THOLONIA_THE_BOOK.html")
    os.system(f"rm {H}/chapters/THOLONIA_THE_BOOK.md")
    os.system(f"mv {H}/chapters/*.pdf {H}/chapters/.pdf")
    os.system(f"mv {H}/chapters/*.epub {H}/chapters/.epub")


# ----------------------------------------------------------------------
# -----------------------------------------------------------------------

STATE = "_prod"
# STATE = "_dev"


argv = sys.argv[1:]

try:
    opts, args = getopt.getopt(argv, "n")

except:
    print("Error")

for opt, arg in opts:
    if opt in ['-n']:
        print(f"NEW VERSION: {update_ver()}")

mkcss()

rebuildmd()  # make new complete MD file

# use this for testing
# os.system(f"cp {H}/chapters/100.md  {H}/chapters/THOLONIA_THE_BOOK.md")

#


pub_prep()
md2html("THOLONIA_THE_BOOK")
html2pdf("THOLONIA_THE_BOOK")
md2epub("THOLONIA_THE_BOOK")

pub_epub()
pub_pdf()
pub_md()
pub_html()
pub_zip()
cleanold()
