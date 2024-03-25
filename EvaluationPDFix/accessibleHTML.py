import sys
import os
import argparse
import timeit
import datetime
import io
import subprocess
import contextlib
import sys

import deepdoctection as dd
import pandas as pd
import numpy as np

from pypdf import PdfReader
from bs4 import BeautifulSoup
from pathlib import Path
from contextlib import redirect_stdout

def load_dataframe(file_path):
    df = pd.read_csv(file_path)

    print("Dataframed loaded...")
    return df[df["dc_type"] == '2e-b']
    

def download_pdf(df_row, file_path):
    url = "https://doi.wooverheid.nl/?doi="
    doi = df_row['dc_identifier']
    Turl = url + doi

    # Download pdf
    command = ["wget", "-q", "--output-document", file_path, Turl]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return print(f"File downloaded to {file_path}")


def set_metadata(df_row, file_path):
    # Set metadata with values from dataframe
    metadata = {
    "title": None,
    "author": None,
    "subject": None,
    "producer": "PDFix",
    "creator": None,
    "creation_date": None,
    "mod_date": None,
    }
    try: 
        if df_row["dc_title"] != np.NaN:
            metadata["title"] = df_row["dc_title"]

        if df_row["dc_publisher_name"] != np.NaN:
            metadata["author"] = df_row["dc_publisher_name"]

        if df_row["dc_description"] != np.NaN:
            metadata["subject"] = df_row["dc_description"]

        if df_row["foi_publishedDate"] != np.NaN:
            metadata["creation_date"] = df_row["foi_publishedDate"]

    except Exception as e:
        print("Error set metadata: " + str(e))


    # Fill metadata with values from original PDF
    try:
        reader = PdfReader(file_path)

        if metadata['title'] == None:
            if hasattr(reader.metadata, 'title') == False:
                metadata['title'] = "Undefined"

        if metadata['author'] == None:
            if hasattr(reader.metadata, 'author') == False:
                metadata['author'] = "Undefined"

        if metadata['subject'] == None:
            if hasattr(reader.metadata, 'description') == False:
                metadata['subject'] = "Undefined"

        if metadata['creator'] == None:
            if hasattr(reader.metadata, 'creator') == False:
                metadata['creator'] = "Undefined"

        if metadata['producer'] == None:
            if hasattr(reader.metadata, 'producer') == False:
                metadata['producer'] = "Undefined"

        if metadata['creation_date'] == None:
            if hasattr(reader.metadata, 'creation_date') == False:
                metadata['creation_date'] = "Undefined"

        if metadata['mod_date'] == None:
            metadata['mod_date'] = datetime.datetime.now()

    except Exception as e:
        print("Error fill metadata: " + str(e))

    print("Metadata set...")
    return metadata


    """Fill missing metadata with metadata from pdf. 
    If no metadata to fill is found 'Undefined' is used."""

    try:
        reader = PdfReader(file_path)

        if metadata['title'] == None:
            if hasattr(reader.metadata, 'title') == False:
                metadata['title'] = "Undefined"

        if metadata['author'] == None:
            if hasattr(reader.metadata, 'author') == False:
                metadata['author'] = "Undefined"

        if metadata['subject'] == None:
            if hasattr(reader.metadata, 'description') == False:
                metadata['subject'] = "Undefined"

        if metadata['creator'] == None:
            if hasattr(reader.metadata, 'creator') == False:
                metadata['creator'] = "Undefined"

        if metadata['producer'] == None:
            if hasattr(reader.metadata, 'producer') == False:
                metadata['producer'] = "Undefined"

        if metadata['creation_date'] == None:
            if hasattr(reader.metadata, 'creation_date') == False:
                metadata['creation_date'] = "Undefined"

        if metadata['mod_date'] == None:
            metadata['mod_date'] = datetime.datetime.now()

    except Exception as e:
        print("Error: " + str(e))

    return metadata


def init_analyzer(pdf_path):
    """Initialize the DeepDoctection analyzer."""
    try:
        analyzer = dd.get_dd_analyzer(config_overwrite=["LANGUAGE='nld'"])
        path = Path.cwd() / pdf_path
        df = analyzer.analyze(path=path)
        doc = iter(df)
    
    except Exception as e:
        print(f"Error init_analyzer: {str(e)}")
    
    print("PDF analyzer initialized...")
    return doc


def build_html(doc, metadata):
    """Creates RML string from analyzed PDF document.
    Returns RML string ready to be converted to accessible HTML."""


    # Create BeautifulSoup object
    html = BeautifulSoup(f'<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//NL" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nl" lang="nl"><head><title>{metadata["title"]}</title></head><body></body></html>', 'html.parser')
    
    # Add metadata
    charset_meta = html.new_tag("meta", charset="UTF-8")
    viewport_meta = html.new_tag("meta")
    viewport_meta["name"] = "viewport"
    viewport_meta["content"] = "width=device-width, initial-scale=1"

    subject_meta = html.new_tag('meta')
    subject_meta["name"] = "subject"
    subject_meta["content"] = metadata["subject"]

    author_meta = html.new_tag('meta')
    author_meta["content"] = metadata["author"]
    author_meta["name"] = "author"
    
    creator_meta = html.new_tag('meta')
    creator_meta["name"] = "creator"
    creator_meta["content"] = metadata["creator"]

    producer_meta = html.new_tag('meta')
    producer_meta["name"] = "producer"
    producer_meta["content"] = metadata["producer"]

    creation_date_meta = html.new_tag('meta')
    creation_date_meta["name"] = "creation_date"
    creation_date_meta["content"] = metadata["creation_date"]

    mod_date_meta = html.new_tag('meta')
    mod_date_meta["name"] = "modification_date"
    mod_date_meta["content"] = metadata["mod_date"]

    html.head.append(charset_meta)
    html.head.append(viewport_meta)
    html.head.append(subject_meta) 
    html.head.append(author_meta)
    html.head.append(creator_meta)
    html.head.append(producer_meta)
    html.head.append(creation_date_meta)
    html.head.append(mod_date_meta)   

    # Add title to body
    title = html.new_tag('H1')
    title.string = metadata["title"]
    html.body.append(title)

    #TODO: Optional* add stylesheet

    # Analyse PDF
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

            # PARAGRAPH
            if page.layouts[y].category_name == "text":
                paragraph = html.new_tag('p')
                paragraph.string = page.layouts[y].text
                html.body.append(paragraph)

            # HEADING
            elif page.layouts[y].category_name == "title":
                heading = html.new_tag('H2')
                heading.string = page.layouts[y].text
                html.body.append(heading)

            # LIST
            elif page.layouts[y].category_name == "list":
                list = html.new_tag('p')
                list.string = page.layouts[y].text
                html.body.append(list)

            # FIGURE
            else:
                print(page.layouts[y].category_name) 
                
        page_number += 1

    print("HTML string build...")
    return html.prettify()


def save_html(html, output_path):
    with open(output_path, "w") as file:
        file.write(html)

    return print(f"File saved to {output_path}")   


if __name__ == '__main__':
    start = timeit.default_timer()

    # Suppress all warnings
    df = load_dataframe('woo_dossiers.csv')

    df_row = df.iloc[1]
    file_path = 'download.pdf'

    # download_pdf(df_row, file_path)

    # Set and fill metadata
    metadata = set_metadata(df_row, file_path)

    # Initialize the PDF analyzer
    document = init_analyzer(file_path)

    # Create the HTML string
    html = build_html(
        doc=document,
        metadata=metadata,
    )

    # Save HTML file
    output_path = 'outputHTML.html'
    save_html(html, output_path)

    print(str(timeit.default_timer() - start) + "s")



