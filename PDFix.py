from metadata import get_metadata
from createTaggedPDF import initAnalyzer, create_rml, create_tagged_pdf

import sys
import os
import argparse


def argumentParse():
    parser = argparse.ArgumentParser(description='PDFix repairs a give PDF document to tagged accessihle PDF.')

    # Add a required argument
    parser.add_argument('-i', '--input', type=str, help='Path to input pdf file.')
    parser.add_argument('-o', '--output', type=str, help='Path to output pdf file.')

    # optional arguments
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force mode', default=False)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the value of the required argument
    return args.input, args.output, args.force


def process_file(input_path, output_path, force_mode):
    # Get the required metadata from the file
    metadata = get_metadata(input_path, force_mode)

    # Initialize the PDF creator
    document = initAnalyzer(input_path)

    # Create the RML string
    filename = os.path.basename(output_path)
    rml = create_rml(
        doc=document,
        metadata=metadata,
        filename=filename
    )

    # Create tagged PDF
    create_tagged_pdf(rml, output_path)



if __name__ == '__main__':
    input_path, output_path, force_mode = argumentParse()

    # Process file
    process_file(input_path, output_path, force_mode)
