
import re
from datetime import datetime

STARTING_COLLEGE_AGE = 18

# OCR: uses LATIN character ﬁ(FI) for spanish ñ.
UNIQUE_LINE_AGE = ['\n\s*\d\d\s{1,3}a(?:n|ﬁ|ñ)os\s*\n', '\n\s*edad.{1,3}\d\d\s*\n', '\n\s*edad.{1,3}\d\d\s{1,3}a(?:n|ﬁ|ñ)os\s*\n']
AGE_IN_TEXT = '(?:edad|tengo).{1,3}\d\d\s{1,3}a(?:n|ﬁ|ñ)os'

MONTHS = {'enero': 1,
          'febrero': 2,
          'marzo': 3,
          'abril': 4,
          'mayo': 5,
          'junio': 6,
          'julio': 7,
          'agosto': 8,
          'septiembre': 9,
          'octubre': 10,
          'noviembre': 11,
          'diciembre': 12,
          'dic': 12,
          'jun.': 6,
          }


def safe_date_time_conversion(year, month, day):
    try:
        return datetime(int(year), int(month), int(day))
    except ValueError:  # date value maybe invalid, will default to the half of the year
        return datetime(int(year), 6, 15)


def parsing_date_format_1(match_obj):
    """Gets a datetime object from a match object. Indices are according to the regex for the date in the text."""
    date_text = match_obj.group()
    elements = date_text.split()
    year = elements[-1]
    month = MONTHS.get(elements[2].lower(), 6)  # if month is not valid then will pick june by default.
    day = elements[0]

    return safe_date_time_conversion(year, month, day)


def parsing_date_format_2(match_obj):
    """Gets a datetime object from a match object with a match like 02/03/1985"""
    date_text = match_obj.group()
    year = re.findall('\d{4}', date_text)[0]
    date_text = date_text.replace(year, '')

    day_month = re.findall('\d{1,2}', date_text)
    month = day_month[1]
    day = day_month[0]

    return safe_date_time_conversion(year, month, day)


def parsing_date_format_3(match_obj):
    """Gets a datetime object from a match object. Indices are according to the regex for the date in the text."""
    date_text = match_obj.group()
    year = re.findall(r'\d{4}', date_text)[0]
    date_text = date_text.replace(year, '')

    month = re.findall(r'\w+', date_text)[0].lower()
    month = MONTHS.get(month, 6)  # if month is not valid then will pick june by default.
    day = re.findall('\d{1,2}', date_text)[0]

    return safe_date_time_conversion(year, month, day)


# Possible regex representing dates and their parsing functions
DATE_FORMATS = {
                # example: 23 de Diciembre de 1990
                r'\d{1,2}\s{1,2}de\s{1,2}\w+(?:\.|,)?\s{1,2}(?:de|del){0,1}\s{0,2}\d\d\d\d': parsing_date_format_1,
                # example: 23/12/1990
                r'[0-3]?[0-9](?!\d).{1}[0-1]?[0-9](?!\d).{1}\d{4}': parsing_date_format_2,
                # example: Diciembre 23 de 1990
                r'\w+ \d{1,2}(?!\d).{0,1} (?:de\s)?\d\d\d\d': parsing_date_format_3,
                }


def years_ago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29  # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)


def age_given_birth(birth):
    """Get age in years given date birth"""
    end = datetime.now()
    num_years = int((end - birth).days / 365.25)
    if birth > years_ago(num_years, end):
        estimated_age = num_years - 1
    else:
        estimated_age = num_years

    if estimated_age >= 16:
        return estimated_age
    else:  # possibly wrong answer
        return None


def find_explicit_age(text):
    """Simple strategy look for the explicit age of the user."""
    matches = re.findall(AGE_IN_TEXT, text, re.IGNORECASE)
    if len(matches) > 0:  # happy case
        return int(re.findall('\d\d', matches[0], re.IGNORECASE)[0])
    else:
        # try unique line patterns.
        for pattern in UNIQUE_LINE_AGE:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if len(matches) > 0:  # happy case
                return int(re.findall('\d\d', matches[0], re.IGNORECASE)[0])

        return None

MIN_REALISTIC_YEAR = 1950


def filter_realistic_years(dates):
    current_year = datetime.now().year
    return [date for date in dates if MIN_REALISTIC_YEAR < date.year <= current_year]


def get_college_starting_age(text):

    current_year = datetime.now().year

    dates = re.findall('(?![a-z])\d\d\d\d(?![a-z])', text, re.IGNORECASE)
    # further clean up
    dates = [datetime(int(re.findall(r'\d\d\d\d', e)[0]), 1, 1) for e in dates]
    dates = filter_realistic_years(dates)

    if len(dates) > 0:
        year_starting_college = min([date.year for date in dates])
        return (current_year - year_starting_college) + STARTING_COLLEGE_AGE
    else:
        return None


def pick_first_date_after_index(dates_indexes, birth_index):

    for idx, possible_date in dates_indexes:
        if birth_index < idx:
            return possible_date

    return None


def find_birth_date(text):
    """Finds the datetime birth date."""

    dates_indexes = []
    for pattern, function in DATE_FORMATS.items():
        dates = re.finditer(pattern, text, re.IGNORECASE)
        dates_indexes += [(m.start(0), function(m)) for m in dates if len(filter_realistic_years([function(m)])) > 0]

    # orders all dates by index ASC.
    dates_indexes = sorted(dates_indexes, key=lambda x: x[0])

    birth_word = re.search(r'nacimiento', text, re.IGNORECASE)

    if birth_word is not None:
        birth_index = birth_word.start()
    else:  # If not birth word present
        # Takes the first result, and trust that it is the one. Birth dates are almost always on document top.
        birth_index = -1

    return pick_first_date_after_index(dates_indexes, birth_index)
