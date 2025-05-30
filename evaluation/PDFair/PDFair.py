import deepdoctection as dd
from pathlib import Path
import re
from YOLO.YOLO import load_and_process_pdf, run_onnx_inference, visualize_boxes

config_overwrite = ["LANGUAGE='nld'",
                    "TEXT_ORDERING.INCLUDE_RESIDUAL_TEXT_CONTAINER=True",
                    "USE_PDF_MINER=True"]
analyzer = dd.get_dd_analyzer(config_overwrite=config_overwrite)


def scale_bbox(bb, original_dpi=72, rendered_dpi=108):
    s = original_dpi / rendered_dpi
    return [bb.ulx * s, bb.uly * s, bb.lrx * s, bb.lry * s]

def calc_centroid(bb):
    return ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)


class Page:
    def __init__(self, pdf, page_number, doc):
        self.pdf = pdf
        self.p = page_number
        self.doc = doc
        self.md = None
        self.header = None

    @staticmethod
    def __doc2md_helper(layout):
        if layout.category_name == "line":
            return f"**{layout.text}**  "
        if layout.category_name == "text":
            return f"{layout.text}  "
        if layout.category_name == "list":
            return "- ".join([item+'\n' for item in re.split('• |[^a-zA-Z]- | |· |[0-9]+\. ', layout.text) if item])
        if layout.category_name == "title":
            return f"## {layout.text}"

    def doc2md(self, skip_headers = False):
        if skip_headers:
            layouts = (l for l in sorted(self.doc.layouts, key=lambda x: x.bounding_box.uly) if not l.is_header)
            self.md = "\n".join(self.__doc2md_helper(layout) for layout in layouts)
            self.header = "\n\n".join(layout.text for layout in self.doc.layouts if layout.is_header)
        else:
            layouts = sorted(self.doc.layouts, key=lambda x: x.reading_order)
            self.md = "\n".join(self.__doc2md_helper(layout) for layout in layouts)
        

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


class Pdf:
    def __init__(self, path):
        self.path = path
        self.pages = None

    def pdf2doc(self):
        df = analyzer.analyze(path=Path.cwd() / self.path)
        pages = iter(df)
        self.pages = [Page(self, i+1, doc) for i, doc in enumerate(pages)]

    

