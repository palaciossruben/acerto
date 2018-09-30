"""
To run do:
python3 document_reader.py
"""
import os
import sys
from django.core.wsgi import get_wsgi_application


# Environment can use the models as if inside the Django app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testing_webpage.settings')
application = get_wsgi_application()

import ntpath
import pickle
from nltk.stem.snowball import SnowballStemmer
import nltk

from subscribe import helper as h
from subscribe import cts
from beta_invite.models import User


VALID_EXTENSIONS = {'.jpg', '.jpeg', '.doc', '.docx', '.png', '.pdf', '.txt'}
INVALID_FOLDERS = ['10587', '9598']  # this folders produce a out of memory error


def get_text(folder_path, doc, extension, fast=True):
    """Gets the text regardless of the extension"""

    filename = os.path.join(folder_path, doc)
    text = ''

    if extension in VALID_EXTENSIONS:
        if extension in {'.jpg', '.png', '.jpeg'}:  # image.
            text = h.get_image_text(filename)
        elif extension in {'.doc', '.docx'}:  # word doc.
            text = h.get_word_text(filename)
        elif extension == '.pdf':
            text = h.get_pdf_text(folder_path, filename, fast=fast)
        elif extension == '.txt':
            text = h.get_text_from_txt_file(filename)

    else:
        h.log('Found invalid or unimplemented extension {}, will not read.'.format(extension))

    return text


def multilingual_stemmer(text):
    """
    This code uses nltk to stem words in multiple langs
    :param text:
    :return:
    """
    eng_stemmer = SnowballStemmer("english", ignore_stopwords=True)
    spa_stemmer = SnowballStemmer("spanish", ignore_stopwords=True)
    # TODO add new lang here

    return ' '.join([spa_stemmer.stem(eng_stemmer.stem(w)) for w in nltk.word_tokenize(text)])


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def read_text_and_save(user, folder_path, parsed_path, parsed_filename, fast=True):
    """Will iterate over all documents from a User and extract all text, then write and return it."""
    text = ''
    filename = path_leaf(user.curriculum_url)
    if filename != parsed_filename:

        # renames any file that has spaces for one with no spaces.
        # because it's easier to execute shell commands.
        filename = h.rename_filename(folder_path, filename)

        extension = os.path.splitext(filename)[1].lower()
        text += get_text(folder_path, filename, extension, fast=fast)

    text = h.remove_accents_and_non_ascii(text).lower()

    # TODO: Activate stemming: adding only the roots of words
    #text = multilingual_stemmer(text)

    with open(parsed_path, 'w', encoding='UTF-8') as f:
        f.write(text)
        h.log('new document: {}'.format(parsed_path))

    return text


def read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename, fast=True):
    """Will iterate over all documents from a User and extract all text, then write and return it."""
    text = ''
    for d in docs:
        if d != '.DS_Store' and d != parsed_filename:

            # renames any file that has spaces for one with no spaces.
            # because it's easier to execute shell commands.
            d = h.rename_filename(folder_path, d)

            extension = os.path.splitext(d)[1].lower()
            text += get_text(folder_path, d, extension, fast=fast)

    text = h.remove_accents_and_non_ascii(text).lower()

    # TODO: Activate stemming: adding only the roots of words
    #text = multilingual_stemmer(text)

    with open(parsed_path, 'w', encoding='UTF-8') as f:
        f.write(text)
        h.log('new document: {}'.format(parsed_path))

    return text


def write_last_updated_at(user):
    """Up until this id all users have been inspected at least once"""
    pickle.dump(user.updated_at, open(cts.LAST_USER_UPDATED_AT, 'wb'))


def read_all(fast=True, force=False):
    """Reads all files inside the resumes folder. Files can have several different extensions.
    :param force: Boolean indicating if the Curriculum have to be read again.
    """
    folders = os.listdir(cts.RESUMES_PATH)

    users = [u for u in User.objects.all().order_by('updated_at')]

    for user in users:
        folder = str(user.id)
        if folder in folders:
            print('analysing folder: {}'.format(folder))
            folder_path = os.path.join(cts.RESUMES_PATH, folder)
            if os.path.isdir(folder_path) and folder not in INVALID_FOLDERS:
                docs = os.listdir(folder_path)

                parsed_filename = '{}.txt'.format(folder)
                parsed_path = os.path.join(folder_path, parsed_filename)

                # Only parses an un-parsed files
                if parsed_filename not in docs or force:
                    #text = read_all_text_and_save(docs, folder_path, parsed_path, parsed_filename, fast=fast)
                    text = read_text_and_save(user, folder_path, parsed_path, parsed_filename, fast=fast)
                    write_last_updated_at(user)
                    user.curriculum_text = text.replace('\x00', '')  # removes char null
                    user.save()


def run():
    with open('document_reader.log', 'a') as f:
        sys.stdout = h.Unbuffered(f)
        read_all(fast=True, force=False)


if __name__ == "__main__":
    read_all(fast=True, force=False)
