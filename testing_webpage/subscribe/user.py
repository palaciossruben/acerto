import re
import nltk
import operator

import age

COLOMBIA = 'Colombia'
ECUADOR = 'Ecuador'
PERU = 'Peru'
CHILE = 'Chile'
MEXICO = 'Mexico'
VENEZUELA = 'Venezuela'
BOLIVIA = 'Bolivia'
ARGENTINA = 'Argentina'

COUNTRIES = {COLOMBIA: ('Bogota',
                        'Medellin',
                        'Cali',
                        'Barranquilla',
                        'Sucre',
                        'Antioquia',
                        'Tunja'),
             ECUADOR: ['Quito'],
             PERU: ('Lima',
                    'Chiclayo'),
             CHILE: ['Santiago de Chile'],
             MEXICO: ['Naucalpan de Juarez'],
             VENEZUELA: ('Carabobo',
                         'Maracay'),
             BOLIVIA: ['La Paz'],
             ARGENTINA: ('Buenos Aires',
                         'Cordoba')
             }


INSTITUTION_KEYWORDS = ['universidad', 'universitaria', 'institucion', 'colegio', 'instituto']

HIGH_SCHOOL = 'high school'
TECHNICAL = 'technical'
UNDERGRADUATE = 'undergraduate'
MASTER = 'masters'
PHD = 'phd'

EDUCATION_LEVELS = {
                    HIGH_SCHOOL: 0,
                    TECHNICAL: 1,
                    UNDERGRADUATE: 2,
                    MASTER: 3,
                    PHD: 4
                    }

# TODO: ideas:
# USE compulsory relations: Soy Tecnologo
# When Institutes of Universities mentioned demand nearby proper names. Alternatively use distance to proper context. 2/60
# Demand University that can by googled.
# screenshots + OCR  max impact: 2/60

EDUCATION_LEVEL_KEYWORDS = {
                            HIGH_SCHOOL: ('colegio', 'estudiante', ),
                            TECHNICAL: ('instituto', 'tecnico', 'tecnologo'),
                            # profesional excludes "Perfil Profesional or Area Profesional" case.
                            UNDERGRADUATE: ('universi(?!dades)', 'pregrado', 'bsc', r'(?!perfil|area|tecnico|resumen|experiencia|proyeccion)(\b\w+\b\s*profesional(?!(es|mente)))|(^\s*profesional)'),
                            MASTER: ('maestria', 'magister', 'master', 'msc'),
                            PHD: ['doctorado']
                            }

MIN_UNDERGRAD_AGE = 22
MIN_TECHNICAL_AGE = 20

# disables the plural of estudiante
UNFINISHED_EDUCATION_KEYWORDS = ['estudiando', 'cursando', 'cursado', 'estudiante(?!s)', 'semestre', '\d\d\d\d.{0,7}actualidad', 'sin diploma']
FINISHED_EDUCATION_KEYWORDS = ['culmina', 'egresad', 'finalizacion', 'finalizado']


class User:

    @staticmethod
    def get_country(text):

        countries_score = dict()

        for country, patterns in COUNTRIES.items():

            # the country itself is a pattern
            patterns = [e for e in patterns] + [country]

            results = [len(re.findall(p, text, re.IGNORECASE)) for p in patterns]

            countries_score[country] = sum(results)

        return max(countries_score.items(), key=operator.itemgetter(1))[0]

    @staticmethod
    def get_institutions(text):

        words = nltk.word_tokenize(text)
        l = len(words)

        institutions = []
        for idx, word in enumerate(words):
            if word.lower() in INSTITUTION_KEYWORDS:
                institutions.append(' '.join(words[idx:min(idx + 3, l)]))

        return tuple(institutions)

    def downgrade_if_not_completed(self, text, level):
        """if more negative than positive words are found then will be downgraded 1 level."""
        negative = [len(re.findall(p, text, re.IGNORECASE)) for p in UNFINISHED_EDUCATION_KEYWORDS]
        positive = [len(re.findall(p, text, re.IGNORECASE)) for p in FINISHED_EDUCATION_KEYWORDS]

        # positive points will count twice. Experimental evidence shows better performance.
        total = sum(positive) - sum(negative)

        new_idx = max(EDUCATION_LEVELS[level] - (total < -1), 0)

        # to be undergrad or more at least be MIN_UNDERGRAD_AGE.
        if new_idx >= EDUCATION_LEVELS[UNDERGRADUATE] and self.age is not None and self.age < MIN_UNDERGRAD_AGE:
            age_undergrad_score = 1
        else:
            age_undergrad_score = 0

        # to be technical or more at least be MIN_TECHNICAL_AGE.
        if new_idx >= EDUCATION_LEVELS[TECHNICAL] and self.age is not None and self.age < MIN_TECHNICAL_AGE:
            age_technical_score = 1
        else:
            age_technical_score = 0

        return new_idx - age_undergrad_score - age_technical_score

    def get_education_level(self, text):

        levels_score = dict()

        for level, patterns in EDUCATION_LEVEL_KEYWORDS.items():

            # the level itself is a pattern
            patterns = [e for e in patterns] + [level]

            results = [len(re.findall(p, text, re.IGNORECASE)) for p in patterns]

            levels_score[level] = (sum(results) > 0) * EDUCATION_LEVELS[level]

        level = max(levels_score.items(), key=operator.itemgetter(1))[0]

        level_number = self.downgrade_if_not_completed(text, level)

        level_names = list(EDUCATION_LEVELS.keys())

        return level_names[level_number]

    @staticmethod
    def get_city(text):
        return 'la'  # TODO: implement

    @staticmethod
    def get_experience(text):

        year_pattern = r'\d\d\d\d.{1,6}\d\d\d\d'
        return

    def get_age(self, text):
        """Tries in this order:
            1. Getting the explicit age (eg. Edad: 26 años)
            2. Getting the birth date (eg nacimiento: 19 de Mayo de 1980)
            3. Infer age from time the subject started college and add 18 years.
            4. Infer age when the user finished college and add 5 years for undergrad and 3 years to technical, plus 18
        """

        explicit_age = age.find_explicit_age(text)

        if explicit_age is None:
            birth_date = age.find_birth_date(text)
            if birth_date is not None:
                return age.age_given_birth(birth_date)
            else:
                return age.get_college_starting_age(text)
        else:
            return explicit_age

    def __init__(self, text, country=None, institutions=(), education_level=None, city=None, experience=None, age=None):
        self.text = text

        if age is None:
            self.age = self.get_age(text)
        else:
            self.age = age

        if country is None:
            self.country = self.get_country(text)
        else:
            self.country = country

        if city is None:
            self.city = self.get_city(text)
        else:
            self.city = city

        if len(institutions) == 0:
            self.institutions = self.get_institutions(text)
        else:
            self.institutions = institutions

        if education_level is None:
            self.education_level = self.get_education_level(text)
        else:
            self.education_level = education_level

        if experience is None:
            self.experience = self.get_experience(text)
        else:
            self.experience = experience
