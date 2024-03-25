import deepdoctection as dd
import xml.etree.ElementTree as ET
import io

from pathlib import Path
from rlextra.rml2pdf import rml2pdf


def initAnalyzer(pdf_path):
    """Initialize the DeepDoctection analyzer."""

    analyzer = dd.get_dd_analyzer(config_overwrite=["LANGUAGE='nld'"])
    path = Path.cwd() / pdf_path
    df = analyzer.analyze(path=path)
    doc = iter(df)
    
    return doc


def get_bbox(layout, page_width, page_height, RL_width, RL_height):
    """Calculates x, y, width and heigth of frame for ReportLab."""

    # Get bbox from layout
    ulx = layout.bounding_box.ulx
    uly = layout.bounding_box.uly
    layout_width = layout.bounding_box.width
    layout_height = layout.bounding_box.height

    # Calculate frame bbox
    y = uly + layout_height

    frame_x1 = ulx / page_width * RL_width
    frame_y1 = RL_height - (y / page_height * RL_height) # inverse because RL starting point is bottom left
    frame_width = (layout_width / page_width * RL_width)
    frame_height = (layout_height / page_height * RL_height)

    return frame_x1, frame_y1, frame_width, frame_height


def create_rml(doc, metadata, filename:str):
    """Creates RML string from analyzed PDF document.
    Returns RML string ready to be converted to tagged PDF."""
    
    width, height = 595, 842

    # Add a DOCTYPE declaration
    doctype_declaration = '<!DOCTYPE document SYSTEM "rml_1_0.dtd">'
    
    # Create the document element
    document = ET.Element("document", {"filename":filename, "compression":"0", "invariant": "1", "tagged":"1"})

    docinit = ET.SubElement(document, "docinit")
    registerTTFont = ET.SubElement(docinit, "registerTTFont", {"faceName":"Helvetica", "fileName":"font/Helvetica.ttf"})
    registerTTFont = ET.SubElement(docinit, "registerTTFont", {"faceName":"Helvetica-Bold", "fileName":"font/HelveticaBold.ttf"})

    # Create the template element
    pageSize = f"({width},{height})" # A4 size 
    template = ET.SubElement(document, "template", {
        "pageSize":pageSize,
        "title":str(metadata['title']),
        "subject":str(metadata['subject']),
        "author":str(metadata['author']),
        "lang":"nl-NL"
        })

    # Create pageTemplate element
    pageTemplate = ET.SubElement(template, "pageTemplate", {"id":"main"})

    # Create stylesheet element
    stylesheet = ET.SubElement(document, "stylesheet")

    paraStyle = ET.SubElement(stylesheet, "paraStyle", {
        "name": "h1",
        "fontName": "Helvetica-Bold",
        "fontSize": "9"
    })

    paraStyle = ET.SubElement(stylesheet, "paraStyle", {
        "name": "para",
        "fontName": "Helvetica",
        "fontSize": "9"
    })

    # Create story element
    story = ET.SubElement(document, "story")

    page_number = 0

    for page in doc:
        # Find the correct reading order
        reading_o_list = []
        index_list = []
        for i in range(len(page.layouts)):
            reading_o_list.append(page.layouts[i].reading_order)
            index_list.append(i)
        
        reading_o_sorted = [x for _, x in sorted(zip(reading_o_list, index_list))]
        
        # Create all the pageTemplate frames
        for y in reading_o_sorted:
            frame_x1, frame_y1, frame_width, frame_height = get_bbox(page.layouts[y], page.width, page.height, width, height)
            
            frame = ET.SubElement(pageTemplate, "frame", {
                "id":f"p{page_number}f{y}", 
                "x1":str(frame_x1), 
                "y1":str(frame_y1), 
                "width":str(frame_width), 
                "height":str(frame_height)
                })
        
            # PARAGRAPH
            if page.layouts[y].category_name == "text":
                keepInFrame = ET.SubElement(story, "keepInFrame", {"onOverflow":"shrink", "id":f"p{page_number}ff{y}", "frame":f"p{page_number}f{y}"})
                para = ET.SubElement(keepInFrame, "para", {"tagType":"P", "style":"para"})
                font = ET.SubElement(para, "font", {"face":"Helvetica"})
                font.text = page.layouts[y].text

            # HEADING
            elif page.layouts[y].category_name == "title":
                keepInFrame = ET.SubElement(story, "keepInFrame", {"onOverflow":"overflow", "id":f"p{page_number}ff{y}", "frame":f"p{page_number}f{y}"})
                heading = ET.SubElement(keepInFrame, "h1", {"tagType":"H1", "style":"h1"})
                font = ET.SubElement(heading, "font", {"face":"Helvetica-Bold"})
                font.text = page.layouts[y].text

            # LIST
            elif page.layouts[y].category_name == "list":
                keepInFrame = ET.SubElement(story, "keepInFrame", {"onOverflow":"shrink", "id":f"p{page_number}ff{y}", "frame":f"p{page_number}f{y}"})
                para = ET.SubElement(keepInFrame, "para", {"tagType":"P", "style":"para"})
                font = ET.SubElement(para, "font", {"face":"Helvetica"})
                font.text = page.layouts[y].text

            # FIGURE
            else:
                print(page.layouts[y].category_name) 
                
                
        nextPage = ET.SubElement(story, "nextPage")
        page_number += 1
        

    # Create the XML tree
    tree = ET.ElementTree(document)

    # Use an in-memory file-like object
    xml_content = io.BytesIO()
    tree.write(xml_content, xml_declaration=False)

    # Get the XML content as bytes
    xml_bytes = xml_content.getvalue()

    # Decode the bytes to a string if needed
    xml_string = doctype_declaration + xml_bytes.decode('utf-8')

    return xml_string


def create_tagged_pdf(RML, outputFilePath):
    """Converts XML string to tagged PDF."""
    
    try:
        rml2pdf.go(RML, outputFilePath)
    
    except Exception as e:
        print(f"Error converting RML to PDF (ReportLab): {str(e)}")
    
    return print(f"PDF converted to {outputFilePath}")