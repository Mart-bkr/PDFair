# PDFix-repo
Tool that fixes accessibility issues of a pdf-file.

### Scripts guide
`PDFix.py` Main file that converts a pdf file to accessible pdf through the command line (using createTaggedPDF.py and metadata.py). 

`createTaggedPDF.py` Script that uses DeepDoctection to analyse the pdf file and uses the structural information to build a tagged accessible PDF in ReportLab.

`metadata.py` Script that checks if metadata is present and prompts user to add missing metadata.

`evaluation/accessibleHTML.py` Script that is used to generate accessible HTML as output instead of PDF. Used in combination with document DataFrame for evaluation purposes. 



