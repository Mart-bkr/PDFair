from pypdf import PdfReader
import datetime


def get_metadata(file_path, force_mode):
    """Return a dictionary with the metadata of a PDF file."""

    metadata = {}

    try:
        reader = PdfReader(file_path)

        if reader.metadata == None:
            if force_mode is True:
                metadata['title'] = 'Undefined'
                metadata['author'] = 'Undefined'
                metadata['subject'] = 'Undefined'
                metadata['creator'] = 'Undefined'
                metadata['producer'] = 'Undefined'
                metadata['mod_date'] = datetime.datetime.now()
            
            else:
                metadata['title'] = input('Insert metadata "Title": ')
                metadata['author'] = input('Insert metadata "Author": ')
                metadata['subject'] = input('Insert metadata "Subject": ')
                metadata['creator'] = input('Insert metadata "Creator": ')
                metadata['producer'] = input('Insert metadata "Producer": ')
                metadata['creation_date'] = datetime.datetime.now()
                metadata['mod_date'] = datetime.datetime.now()      

        else:
            metadata['title'] = reader.metadata.title
            metadata['author'] = reader.metadata.author
            metadata['subject'] = reader.metadata.subject
            metadata['creator'] = reader.metadata.creator
            metadata['producer'] = reader.metadata.producer
            metadata['creation_date'] = reader.metadata.creation_date
            metadata['mod_date'] = reader.metadata.modification_date

            if force_mode is True:
                if metadata['title'] is None:
                    metadata['title'] = 'Undefined'
                if metadata['author'] is None:
                    metadata['author'] = 'Undefined'
                if metadata['subject'] is None:
                    metadata['subject'] = 'Undefined'
                if metadata['creator'] is None:
                    metadata['creator'] = 'Undefined'
                if metadata['producer'] is None:
                    metadata['producer'] = 'Undefined'
                if metadata['mod_date'] is None:
                    metadata['mod_date'] = datetime.datetime.now()

            else: 
                if metadata['title'] is None:
                    metadata['title'] = input('Insert metadata "Title": ')
                if metadata['author'] is None:
                    metadata['author'] = input('Insert metadata "Author": ')
                if metadata['subject'] is None:
                    metadata['subject'] = input('Insert metadata "Subject": ')
                if metadata['creator'] is None:
                    metadata['creator'] = input('Insert metadata "Creator": ')
                if metadata['producer'] is None:
                    metadata['producer'] = input('Insert metadata "Producer": ')
                if metadata['mod_date'] is None:
                    metadata['mod_date'] = datetime.datetime.now()

    except Exception as e:
        print("Error: " + str(e))

    return metadata


def fill_metadata(file_path, metadata):
    try:
        reader = PdfReader(file_path)

        if metadata['title'] == None:
            if hasattr(reader.metadata, 'title') == f:
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
