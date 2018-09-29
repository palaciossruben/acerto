import os
import io
import re
import nltk
import shutil
import PyPDF2
import pickle
import zipfile
import textract
import subprocess
import unicodedata
import pytesseract

from datetime import datetime
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from shutil import copyfile
from PIL import Image


def get_image_text(filename):
    """outputs text from an image with tessarect-OCR"""

    try:
        im = Image.open(filename)
        tmp_path = os.path.join('media/resumes', 'tmp.jpg')
        im.save(tmp_path)
    except OSError:  # OSError: cannot identify image file ...
        return ''

    try:
        text = pytesseract.image_to_string(Image.open(tmp_path))#, lang='spa')
    except OSError:  # Error: image file is truncated (8 bytes not processed)
        return ''
    except pytesseract.pytesseract.TesseractError:
        return ''

    # TODO: add spell check/correction

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

    try:
        subprocess.run(command, shell=True)

        text = ''
        # only reads up to 2 images: usually when there are many, they have no content and take too much time.
        images = os.listdir(images_path)
        for image in images[:min(2, len(images))]:
            text += get_image_text(os.path.join(images_path, image))
        return text
    except OSError:  # [Errno 12] Cannot allocate memory
        return ''


def get_word_text(filename):
    """outputs text from .docx document"""
    print('word .doc')
    try:
        text = textract.process(filename).decode("utf-8")
    except:  # Textract is buggy as shit, better just to pass any error.
        text = ''
    
    # If not enough info found will try with OCR on the doc images.
    # Get text from image trick: 1. rename to zip, 2. uncompress, 3. look inside.
    if len(text) < 100:
        print('did ocr to .doc')
        zip_folder = os.path.splitext(filename)[0]
        zip_filename = zip_folder + '.zip'
        copyfile(filename, zip_filename)

        try:
            zip_ref = zipfile.ZipFile(zip_filename, 'r')
        except zipfile.BadZipFile:  # can fail with: Bad magic number for central directory
            return ''

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


# TODO: Solve for different languages
def text_has_no_data(text):
    """
    Finds if there is meaningful data on the text.
    Args:
        text: string.
    Returns:
    """

    has_no_data = len(text.replace('\n', '').replace(' ', '')) == 0
    if has_no_data:
        return True  # empty file found
    else:  # Try finding meaning
        words = nltk.word_tokenize(text)

        # make it faster by using my own relevance dictionary
        with open(os.path.join('subscribe', 'es-MX.dic'), 'r', encoding='UTF-8') as vocabulary_file:

            dictionary_text = remove_accents_and_non_ascii(vocabulary_file.read())
            vocabulary = nltk.word_tokenize(dictionary_text)

            for w in words:
                if w in vocabulary:
                    return False  # Found valid word

        # Found no Spanish words
        return True


def get_image_num_name(image, count):
    return '{}-{}.png'.format(image, count)


def get_pdf_text_with_ocr(filename):
    """Convert to png and use OCR, this is a last resort."""

    image_basename = os.path.splitext(filename)[0]

    # create file, just so that the next command will not fail.
    open(image_basename, 'w').close()

    # converts each page to an image.
    command = 'pdftoppm -png {filename} {image}'.format(filename=filename, image=image_basename)

    try:
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
    except OSError:  # [Errno 12] Cannot allocate memory
        return ''


def get_text_with_traditional_strategy(folder_path, filename):
    """
    Follows path from greater chance of success to least.
    This is not perfect. Some tricky PDFS can join all words or separate every other character.
    Args:
        folder_path:
        filename:
    Returns: String with text
    """
    text = get_pdf_text_pdf_miner(filename)
    if text_has_no_data(text):
        try:
            text = get_pdf_text_pypdf2(filename)
        except:
            text = ''

    # Still nothing; then take out the big gun. Convert to png and use OCR
    if text_has_no_data(text):
        text = get_pdf_text_with_ocr(filename)
    else:  # If things are OK still some images might be missing:
        text += get_text_from_pdf_images(folder_path, filename)

    return text


def get_relevance_index(text, relevance_dictionary):

    total_relevance = 0
    for word, relevance in relevance_dictionary.items():
        repetitions = len(re.findall('(^|\s|\n){word}(^|\s|\n)'.format(word=word), text.lower()))
        total_relevance += repetitions*relevance

    return total_relevance


def get_text_with_relevance_index(folder_path, filename, relevance_dictionary):
    """
    Calculates relevance index for each strategy and goes with the one that has a higher payoff.
    Args:
        folder_path:
        filename:
        relevance_dictionary: A dict which keys are words and which values are the relevance score.
    Returns: string
    """
    # chooses strategy that maximizes relevance index
    pdf_miner_text = get_pdf_text_pdf_miner(filename)

    # Unfortunately it can fail for no apparent reason.
    try:
        pypdf_text = get_pdf_text_pypdf2(filename)
    except:
        pypdf_text = ''

    ocr_text = get_pdf_text_with_ocr(filename)

    pdf_miner_index = get_relevance_index(pdf_miner_text, relevance_dictionary)
    pypdf_index = get_relevance_index(pypdf_text, relevance_dictionary)
    ocr_index = get_relevance_index(ocr_text, relevance_dictionary)

    print('relevances are, miner: {} pypdf: {} ocr: {}'.format(pdf_miner_index, pypdf_index, ocr_index))

    if max(pdf_miner_index, pypdf_index, ocr_index) == pdf_miner_index:
        text = pdf_miner_text
        text += get_text_from_pdf_images(folder_path, filename)
        print('wins miner')
    elif max(pypdf_index, ocr_index) == pypdf_index:
        text = pypdf_text
        text += get_text_from_pdf_images(folder_path, filename)
        print('wins pypdf')
    else:
        text = ocr_text
        print('wins ocr')

    return text


def get_pdf_text(folder_path, filename):
    """Tries different libraries"""
    print('on a .pdf')

    # Opens word_user_dict, or returns unordered users.
    try:
        relevance_dictionary = pickle.load(open('subscribe/relevance_dictionary.p', 'rb'))
        return get_text_with_relevance_index(folder_path, filename, relevance_dictionary)
    except FileNotFoundError:
        print('traditional strategy')
        return get_text_with_traditional_strategy(folder_path, filename)


def remove_accents_in_string(element):
    """
    Removes accents and non-ascii chars
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        text = ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
        # removes non ascii chars
        text = ''.join([i if ord(i) < 128 else '' for i in text])

        return text.replace('\x00', '')  # remove NULL char
    else:
        return element


def remove_accents_and_non_ascii(an_object):
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
    elif isinstance(an_object, set):
        return set([remove_accents_in_string(e) for e in an_object])
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


def get_text_from_txt_file(filename):
    try:
        return open(filename).read()
    except UnicodeDecodeError:
        return ''


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def log(s):
    print('{}: {}'.format(datetime.today(), s))
