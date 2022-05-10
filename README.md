# NameTag_generator
Python 3 script to generate nametags for events: it takes in input a CSV file with first name, last name and affiliation (separator is ';' to allow commas in affiliations) and outputs a PDF with the name tags.

Each name tag is based on the template 'template_tag.svg', with the tag fields replaced with the data from the CSV file; the script automatically shrinks the text size in case the text does not fit within the tag.

WARNING: Inkscape and Latex are called asynchronously. When launching the script for the first time it might fail as Latex is called before all nametags have been generated. Be patient and call the script again after all files have been created!

To use it:

python3 tag_generator.py input.csv

The file 'example.csv' is provided as an example.

**Note**: UTF8 characters from names are rendered within SVG (=text) and PDF files, so there shouldn't be issues with most European characters including those of Italian (accented characters), French (çedille), German (Umlauts) and so on. Characters from other alphabets (e.g. Turkish, Hungarian, Danish, ...) are untested: beware and check!

Dependencies:

* inkscape, to convert svg tags into PDF for LaTeX inclusion
* pdflatex, to compile the final PDF documents with the name tags

WARNING: About 500MB of space are required to install the dependencies!

```
sudo apt install inkscape
sudo apt install texlive-latex-base
sudo apt install libcanberra-gtk-module libcanberra-gtk3-module
sudo apt-get install texlive-latex-extra
```

Basic functioning:

* read SVG template
* for each line in CSV
    * parse tag information
    * replace tag info inside the SVG template fields
    * adapt the text size
    * output an SVG file, which contains a single tag
* convert all SVG tags into PDF files
* include all PDF files into a LaTeX file as subpictures (two subpictures per picture)
* compile LaTeX into printable PDF
* remove all intermediate files
