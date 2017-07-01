import os
import io
import shutil
import PyPDF2
import textract
import subprocess
import unicodedata
import pytesseract

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from shutil import copyfile
from PIL import Image, ImageEnhance, ImageFilter

from cts import *


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


def get_text_from_pdf_images(folder_path, pdf_path):
    """For this solution to work, first install poppler with apt-get or homebrew respectively."""

    images_path = os.path.join(folder_path, 'pdf_images')

    if not os.path.exists(images_path):
        os.makedirs(images_path)
    else:  # clean dir before writing anything new.
        shutil.rmtree(images_path)
        os.makedirs(images_path)

    command = 'pdfimages {} {}'.format(pdf_path, os.path.join(images_path, 'image'))

    subprocess.run(command, shell=True)

    text = ''
    # only reads up to 10 images: usually when there are many, they have no content and take too much time.
    images = os.listdir(images_path)
    for image in images[:min(10, len(images))]:
        text += get_image_text(os.path.join(images_path, image))

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


def get_pdf_text_pdf_miner(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    try:
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                      password=password,
                                      caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()
    except:
        text = ''

    fp.close()
    device.close()
    retstr.close()
    return text


def get_pdf_text_pypdf2(filename):
    text = ''
    pdf_reader = PyPDF2.PdfFileReader(open(filename, 'rb'))  # 'rb' for read binary mode

    for page in range(pdf_reader.numPages):
        page_obj = pdf_reader.getPage(page)
        text += page_obj.extractText()

    return text


def text_has_no_data(text):
    """Filters for many '\n' cases """
    return len(text.replace('\n', '').replace(' ', '')) == 0


def get_image_num_name(image, count):
    return '{}-{}.png'.format(image, count)


def last_chance(filename):
    """Convert to png and use OCR, this is  a last resort."""

    image_basename = os.path.splitext(filename)[0]

    # create file, just so that the next command will not fail.
    open(image_basename, 'w').close()

    # converts each page to an image.
    command = 'pdftoppm -png {filename} {image}'.format(filename=filename, image=image_basename)
    subprocess.run(command, shell=True)

    # removes unnecessary file
    os.remove(image_basename)

    # Reads with OCR whatever pages the poppler converted to png.
    count = 1
    text = ''
    image_num = get_image_num_name(image_basename, count)
    while os.path.exists(image_num):
        text += get_image_text(image_num)
        os.remove(image_num)
        count += 1
        image_num = get_image_num_name(image_basename, count)

    return text


def get_pdf_text(folder_path, filename):
    """Tries different libraries"""
    text = get_pdf_text_pdf_miner(filename)
    if text_has_no_data(text):
        try:
            text = get_pdf_text_pypdf2(filename)
        except:
            text = ''

    # Still nothing; then take out the big gun. Convert to png and use OCR
    if text_has_no_data(text):
        text = last_chance(filename)

    text += get_text_from_pdf_images(folder_path, filename)

    return text


def remove_accents_in_string(element):
    """
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        return ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
    else:
        return element


def remove_accents(an_object):
    """
    Several different objects can be cleaned.
    Args:
        an_object: can be list, string, tuple and dict
    Returns: the cleaned obj, or a exception if not implemented.
    """
    if isinstance(an_object, str):
        return remove_accents_in_string(an_object)
    elif isinstance(an_object, list):
        return [remove_accents_in_string(e) for e in an_object]
    elif isinstance(an_object, tuple):
        return tuple([remove_accents_in_string(e) for e in an_object])
    elif isinstance(an_object, dict):
        return {remove_accents_in_string(k): remove_accents_in_string(v) for k, v in an_object.items()}
    else:
        raise NotImplementedError


def rename_filename(folder_path, filename):
    """Removes accents and spaces to have a easier time later"""

    replacement = {' ': '_', '(': '_', ')': '_'}

    for my_char, replace_char in replacement.items():

        if my_char in filename:
            new_name = filename.replace(my_char, replace_char)
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))
            filename = new_name

    new_name = ''.join(c for c in unicodedata.normalize('NFD', filename)
                       if unicodedata.category(c) != 'Mn')
    os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))

    return new_name
