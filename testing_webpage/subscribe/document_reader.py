import os
import sys
#from subscribe import helper as h
import helper as h

RESUMES_PATH = '../media/resumes'
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.doc', '.docx', '.png', '.pdf', '.txt'}


def get_text(folder_path, doc, extension):
    """Gets the text regardless of the extension"""

    filename = os.path.join(folder_path, doc)
    text = ''

    if extension in VALID_EXTENSIONS:
        if extension in {'.jpg', '.png', '.jpeg'}:  # image.
            text = h.get_image_text(filename)
        elif extension in {'.doc', '.docx'}:  # word doc.
            text = h.get_word_text(filename)
        elif extension == '.pdf':
            text = h.get_pdf_text(folder_path, filename)
        elif extension == '.txt':
            text = h.get_text_from_txt_file(filename)

    else:
        h.log('Found invalid or unimplemented extension {}, will not read.'.format(extension))

    return text


def read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename):
    """Will iterate over all documents from a User and extract all text, then write and return it."""
    text = ''
    for d in docs:
        if d != '.DS_Store' and d != parsed_filename:
            # renames any file that has spaces for one with no spaces.
            # because it's easier to execute shell commands.
            d = h.rename_filename(folder_path, d)

            extension = os.path.splitext(d)[1]
            text += get_text(folder_path, d, extension)

    text = h.remove_accents(text)

    with open(parsed_path, 'w', encoding='UTF-8') as f:
        f.write(text)
        h.log('new document: {}'.format(parsed_path))

    return text


def read_all(force=False):
    """Reads all files inside the resumes folder. Files can have several different extensions.
    :param force: Boolean indicating if the Curriculums have to be read again.
    """
    resumes_folders = os.listdir(RESUMES_PATH)

    for folder in sorted(resumes_folders):
        print(folder)
        folder_path = os.path.join(RESUMES_PATH, folder)
        if os.path.isdir(folder_path):
            docs = os.listdir(folder_path)

            parsed_filename = '{}.txt'.format(folder)
            parsed_path = os.path.join(folder_path, parsed_filename)
            # Will used saved version, to save time parsing.
            if parsed_filename not in docs or force:
                read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename)


def run():
    #sys.stdout = h.Unbuffered(open('document_reader.log', 'a'))
    read_all(force=False)


if __name__ == "__main__":
    run()
