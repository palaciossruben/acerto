import os
import re
import PyPDF2
import operator
import textract
import subprocess
import pytesseract
import unicodedata

from shutil import copyfile
from PIL import Image, ImageEnhance, ImageFilter

RESUMES_PATH = 'resumes'
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.doc', '.docx', '.png', '.pdf'}


def get_text_from_pdf_images(folder_path, pdf_path):
    """For this solution to work, first install poppler with apt-get or homebrew respectively."""

    images_path = os.path.join(folder_path, 'pdf_images')

    if not os.path.exists(images_path):
        os.makedirs(images_path)

    command = 'pdfimages {} {}'.format(pdf_path, os.path.join(images_path, 'image'))

    subprocess.run(command, shell=True)

    text = ''
    for image in os.listdir(images_path):
        text += get_image_text(os.path.join(images_path, image))

    return text


def get_pdf_text(folder_path, filename):
    text = ''
    pdf_reader = PyPDF2.PdfFileReader(open(filename, 'rb'))  # 'rb' for read binary mode

    for page in range(pdf_reader.numPages):
        page_obj = pdf_reader.getPage(page)
        text += page_obj.extractText()

    text += get_text_from_pdf_images(folder_path, filename)

    return text


def get_word_text(filename):
    """outputs text from .docx document"""

    text = textract.process(filename).decode("utf-8")

    # If not enough info found will try with OCR on the doc images.
    # Get text from image trick: 1. rename to zip, 2. uncompress, 3. look inside.
    if len(text) < 100:
        zip_folder = os.path.splitext(filename)[0]
        zip_filename = zip_folder + '.zip'
        copyfile(filename, zip_filename)

        import zipfile
        zip_ref = zipfile.ZipFile(zip_filename, 'r')
        zip_ref.extractall(zip_folder)
        zip_ref.close()

        images_folder = os.path.join(zip_folder, 'word/media')

        if os.path.isdir(images_folder):
            images = os.listdir(images_folder)

            for i in images:
                image_path = os.path.join(images_folder, i)
                text += get_image_text(image_path)

    return text


def get_image_text(filename):
    """outputs text from an image with tessarect-OCR"""
    im = Image.open(filename)
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')

    tmp_path = os.path.join(RESUMES_PATH, 'tmp.jpg')
    im.save(tmp_path)
    text = pytesseract.image_to_string(Image.open(tmp_path))#, lang='spa')
    return text


def get_text(folder_path, doc, extension):
    """Gets the text regardless of the extension"""

    filename = os.path.join(folder_path, doc)
    text = ''

    if extension in VALID_EXTENSIONS:
        if extension in {'.jpg', '.png', '.jpeg'}:  # image.
            text = get_image_text(filename)
        elif extension in {'.doc', '.docx'}:  # word doc.
            text = get_word_text(filename)
        elif extension == '.pdf':
            text = get_pdf_text(folder_path, filename)
        elif extension == '.txt':
            text = open(filename).read()
    else:
        print('Found invalid or unimplemented extension {}, will not read.'.format(extension))

    return text


class User:

    @staticmethod
    def get_country(text):

        # TODO: strip accents to all text with known code.
        countries = {'Colombia': ['Colombia',
                                  'Bogotá',
                                  'Bogota',
                                  'Medellín',
                                  'Cali',
                                  'Barranquilla',
                                  'Sucre',
                                  'Antioquia',
                                  'Tunja'],
                     'Ecuador': ['Ecuador',
                                 'Quito'],
                     'Perú': ['Perú',
                              'Peru',
                              'Lima',
                              'Chiclayo'],
                     'Chile': ['Chile',
                               'Santiago de Chile'],
                     'México': ['Naucalpan de Juarez'],
                     'Venezuela': ['Venezuela',
                                   'Carabobo',
                                   'Maracay'],
                     'Bolivia': ['Bolivia', 'La Paz'],
                     'Argentina': ['Argentina', 'Buenos Aires', 'Córdoba', 'Cordoba']}

        countries_score = dict()

        for country, patterns in countries.items():
            results = [len(re.findall(p, text, re.IGNORECASE)) for p in patterns]

            countries_score[country] = sum(results)

        return max(countries_score.items(), key=operator.itemgetter(1))[0]

    def __init__(self, text):
        self.text = text
        self.country = self.get_country(text)


def rename_filename(folder_path, filename):
    """Removes accents and spaces to have a easier time later"""

    replacement = {' ': '_'}

    for my_char, replace_char in replacement.items():

        if my_char in filename:
            new_name = filename.replace(my_char, replace_char)
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
            filename = new_name

    new_name = ''.join(c for c in unicodedata.normalize('NFD', filename)
                       if unicodedata.category(c) != 'Mn')
    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))

    return new_name


def read_all():
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
            if parsed_filename in docs:
                text = open(parsed_path, 'r').read()
            else:
                text = ''
                for d in docs:
                    if d != '.DS_Store':
                        # renames any file that has spaces for one with no spaces.
                        # as it is easier to execute shell commands.
                        d = rename_filename(folder_path, d)

                        extension = os.path.splitext(d)[1]
                        text += get_text(folder_path, d, extension)

                # saves parsed text:
                text_file = open(parsed_path, 'w')
                text_file.write(text)
                text_file.close()

            final_dict[folder] = User(text)
            print('done with folder: {}'.format(folder))

    return final_dict


if __name__ == "__main__":
    my_dict = read_all()

    for key, user in my_dict.items():
        print('folder {}, summary:'.format(key))
        print(user.country)
