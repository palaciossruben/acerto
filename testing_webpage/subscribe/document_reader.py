import os
import helper as h

from user import User
from cts import *


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
            text = open(filename).read()
    else:
        print('Found invalid or unimplemented extension {}, will not read.'.format(extension))

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

    with open(parsed_path, 'w') as f:
        f.write(text)

    return text


def read_all(force=False):
    """Reads all files inside the resumes folder. Files can have several different extensions."""
    resumes_folders = os.listdir(RESUMES_PATH)
    final_dict = dict()

    for folder in resumes_folders:
        folder_path = os.path.join(RESUMES_PATH, folder)
        if os.path.isdir(folder_path):
            docs = os.listdir(folder_path)

            parsed_filename = '{}.txt'.format(folder)
            parsed_path = os.path.join(folder_path, parsed_filename)
            # Will used saved version, to save time parsing.
            if parsed_filename in docs and not force:
                with open(parsed_path, 'r') as f:
                    text = f.read()
            else:
                text = read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename)

            if folder == '53':
                a=0
            final_dict[folder] = User(text)
            print('done with folder: {}'.format(folder))

    return final_dict


if __name__ == "__main__":
    my_dict = read_all(force=False)

    for key, user in my_dict.items():
        print('folder {}, summary:'.format(key))
        print(user.country)
        print(user.institutions)
        print(user.education_level)
        print('age: ' + str(user.age))