Process:

**Build Index DB**

- `cd ~/books/tholonia/bin/indexer`

- get marked words checked against the database `./make_regex.py -l`

- add new words listed  and manually edit in DB

- update publish chapters `./make_regex.py -u`

- rebuild underlined docs `./make_regex.py -m` (**make sure you have updated/published you recent work!!**)

**Build document**

- `cd ~/books/tholonia/bin`
- `./publish.py -f`
  - `-n` new version
  - `-f` full publish (defaults to test-publish)

**Build index**‘’“”

- notes:

  - ***Make sure index.toml has the correct page references for the chapters***

  - hyphenate words that have sub-words, “dark matter” -> “dark-matter”

  - use word before key work for identifying a concept: 
    - “French mathematician Joseph Fourier” -> “French mathematician”

- `cd ~/books/tholonia/bin/indexer/`

- Build javascript/html index pages`./indexitems.py`

- Rebuild index DB:`./indexitems.py -r`

- manually print page to PDF files to 

  ​	`Index.pdf` and 

  ​	`Index-by-Category.pdf` 

  in `~/books/tholonis.bin/indexer/pdf`

- `./croppng.py`

- Rebuild book with new indexes. 

  - `cd ~/books/tholonia/bin && ./publish.py -f`

    


### Adding new items

`alias ins="./indexitems_new.py "`

`ins --header People --word 'Zhuang Zhou' --chapter 3 --display 'Zhou, Zhuang; philosopher'`

### Making new index

`./indexitems.py` 

`./croppng.py`  

### Misc

marked-up docs in `/home/jw/books/tholonia/chapters/INDEXED`.  These are the files to edit.

`./make_regex.py --update` # clear the markup only on publishable docs
`./make_regex.py --clear` # clear all index markup in working docs
`./make_regex.py --mark` # create markup based on DB entries 
`./make_regex.py --list` # list all words marked for indexing on DB entries



