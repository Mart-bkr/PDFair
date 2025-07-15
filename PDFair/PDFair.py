"""
PDFair.py

Main class for converting WOO PDF documents to markdown using DeepDoctection.
Performs layout-aware extraction with support for header removal.

This is the core module. Additional modules extend its functionality.

Author: Martijn Bastiaan Bakker
Date: 15-07-2025
"""

import deepdoctection as dd
from pathlib import Path
import re
from YOLO.YOLO import load_and_process_pdf, run_onnx_inference
from itertools import islice

# Configuration settings
config_overwrite = ["LANGUAGE='nld'",  # Dutch as language
                    "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=True",  # controls whether orphan words (those not assigned to any layout segment) should be included in the output.
                    "USE_PDF_MINER=True"]  # When processing a PDF file, it will first try to extract words using pdfplumber
analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)

# Keywords that are always a header
header_keywords_woobesluit = set([
    'Wijze van openbaarmaking en publicatie',
    'afschrift aan belanghebbendenaangetroffen documenten',
    'beoordeling van het bezwaar',
    'beoordeling van uw verzoek',
    'besluit',
    'bezwaarclausulezienswijzen',
    'conclusie',
    'inventarisatie documenten',
    'meer informatie',
    'overwegingen',
    'procedurewettelijk kader',
    'uw verzoek',
    'verloop van de procedure',
    'vragen',
    'wijze van openbaarmaking en plaatsing op internet',
    'wijze van openbaarmaking en publicatiewijze van openbaarmakingplaatsing op internet',
    'zienswijze derde-belanghebbende',
    'zienswijzen'])

header_keywords_beslisnota = set([
    'aanleiding',
    'advies',
    'bijlagen',
    'geadviseerd besluit',
    'informatie die niet openbaar gemaakt kan worden',
    'informatie die niet openbaar wordt gemaakt',
    'kern',
    'kernpunten',
    'politieke context',
    'toelichting'])

header_keywords = header_keywords_woobesluit | header_keywords_beslisnota

# Scale bounding boxes to appropiate size
def scale_bbox(bb, original_dpi=72, rendered_dpi=108):
    s = original_dpi / rendered_dpi
    return [bb.ulx * s, bb.uly * s, bb.lrx * s, bb.lry * s]

# Calculate the centroid of a bounding box
def calc_centroid(bb):
    return ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)

# Represents a single page of a PDF
class Page:
    def __init__(self, pdf, page_number, doc):
        self.pdf = pdf  # parent PDF
        self.p = page_number
        self.doc = doc  # Deepdoctection output
        self.md = None  # Generated markdown for body text
        self.header = None  # Generated markdown for header text

    # Convert doc layout to markdown
    @staticmethod
    def __doc2md_helper(layout):
        if layout.category_name in ["line", "text"]:
            if len(layout.text) <= 100:
                if layout.text.lower().strip() in header_keywords:
                    return f"## {layout.text}\n"
            return f"{layout.text}\n\n"
        if layout.category_name == "list":
            return "\n* " + "* ".join([item+'\n' for item in re.split('o |• |[^a-zA-Z]- | |· |[0-9]+\. ', layout.text) if item])
        if layout.category_name == "title":
            return f"## {layout.text}\n"

    # Convert deepdoctection output to markdown
    def doc2md(self, skip_headers = False):
        if skip_headers:
            layouts = (l for l in sorted(self.doc.layouts, key=lambda x: x.bounding_box.uly) if not l.is_header)
            self.md = "\n".join(self.__doc2md_helper(layout) for layout in layouts)
            self.header = "\n\n".join(layout.text for layout in self.doc.layouts if layout.is_header)
        else:
            layouts = sorted(self.doc.layouts, key=lambda x: x.reading_order)
            self.md = "\n".join(self.__doc2md_helper(layout) for layout in layouts)
        
    # Mark text as header using YOLO model
    def detect_header(self):
        images = load_and_process_pdf(self.pdf.path, page=self.p)
        output_boxes = run_onnx_inference(images[0])

        for l in self.doc.layouts:
            l.is_header = False
            bb = scale_bbox(l.bounding_box)
            x, y = calc_centroid(bb)
            for ob in output_boxes:
                if (ob[0] <= x <= ob[2] and ob[1] <= y <= ob[3]):
                    l.is_header = True


# Represents a single PDF
class Pdf:
    def __init__(self, path):
        self.path = path  # File path
        self.pages = None  # A list of page classes

    def pdf2doc(self, max=None):
        df = analyzer.analyze(path=Path.cwd() / self.path)
        pages = islice(iter(df), max) if max else iter(df)
        self.pages = [Page(self, i+1, doc) for i, doc in enumerate(pages)]
