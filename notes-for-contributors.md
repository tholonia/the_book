The markdown used for this book is not fully compatible with the GitHub flavor of markdown.  This book was assembled with Typora (https://typora.io/), and, as you will see if you look at the markdown pages directly on GitHub, there are some formatting options that do not display correctly.    If you are going to make edits, you'll probably need Typora.

_Other Notes:_

Formatting is controlled by the CSS files in /Styles. The main CSS is ```common_book_prod.css.less```, and from this are created (by the  [publish.py script ](https://github.com/tholonia/the-book/blob/master/bin/publish.py) script).

- common_book_prod.css
  
  - CSS that is used in the PDF, HTML, and ePub
- common_book_prod_header.css
  
  - CSS embedded in the header for HTML and ePub
- epub_prod.css
  
- Overrides just for ePub
  
- epub_prod_header.css
  
  - Overrides for ePub that are embedded in the headers
  

*Note, there is a ```prod/dev``` flag in the script. Using ```dev``` creates a  6.69in x 9.61in page on an A4 size paper.*

The layout for the HTML and PDF is in ```Styles/tholonia.html5```, and for the ePub, ```Styles/tholonia.epub3```. These mainly control the title page. 

```Styles/github.user.css``` is the these for Typora (which is by default `~/.config/Typora/themes/git.user.base.css`)

The ``` kobo_extra.css``` is the CSS that has to be placed in the root directory of the Kobo H2O reader (and imported with Caliber) is you want the CSS to be applied.

If you want to create the PDF, ePub, and HTML output from the markdown, take a look at [python publishing script ](https://github.com/tholonia/the-book/blob/master/bin/publish.py) that was built to do just that. It's a bit iof a pain, and a mess, but at least it will show the arguments needed for Pandoc and PrinceXML (for Arch Linux). The somewhat convoluted publishing script process is:

```mkcss()```

- Build the various versions of the CSS form the LESS files

```rebuildmd()```

- Combine all the chapters in one doc.  The doc must be split into chapters because it is too large for Typora to process correctly.

```md2html("THOLONIA_THE_BOOK")```

- Use Pandoc to create an HTML from the Markdown.  This is necessary as Pandoc does some formatting that is later required for PDF

```html2pdf("THOLONIA_THE_BOOK")```

- Use prince-book to create the PDF from the HTML, which is used because Pandoc doesn't support "margin-inside" CSS property needed to gutter-only margins.

```md2epub("THOLONIA_THE_BOOK")```

- The ePub can be made directly from the Markdown with Pandoc

```pub_prep()```

- Clean up the old versions of stuff before creating new versions.

```pub_epub()
pub_pdf()
pub_md()
pub_html()
pub_zip()
cleanold()
```

- Prepare and move all new versions to ```Latest``` folder

Use 6.69in x 9.61in (16.99cm x 24.4cm) book size.

In Typora, curly brackets, ellipses, and just about anything that is not specifically alphanumeric needs to be represented with HTML codes, such as ```&rdquo; &ldquo; &rsquo; &lsquo; &pi; &hellips; &times; ```, etc., because sometimes Typora gets confused and rewrites these characters if you type them in directly. This may be a bug that gets fixed.

Latex conversion works find in MD to HTML, but fails in HTML to PDF, so any latex needs to be converted to images and manually inserted.  I use  https://latex.codecogs.com/ to create SVG images.

Any questions can be sent to duncan.stroud@gmail.com

