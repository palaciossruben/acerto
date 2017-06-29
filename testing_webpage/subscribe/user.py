import re
import nltk
import operator

import age_module
from cts import *

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

EDUCATION_DURATIONS = {
                       HIGH_SCHOOL: 18,
                       TECHNICAL: 3,
                       UNDERGRADUATE: 5,
                       MASTER: 2,
                       PHD: 4,
                       }

EDUCATION = {
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

EDUCATION_KEYWORDS = {
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

# General professions.
DESIGN = 'design'
ARTS = 'art'
OPERATOR = 'operator'
ENGINEERING = 'engineering'
TECHNICAL_TRADES = 'technical_trades'
ARCHITECTURE = 'architecture'
BUSINESS = 'business_and_economics'
SCIENCE = 'science'
MARKETING = 'marketing'
SOCIAL_SCIENCE = 'social_science'
HEALTH_SCIENCES = 'health_sciences'
PSYCHOLOGY = 'psychology'
COMMUNICATION = 'communication'
LAW_AND_POLITICAL_SCIENCE = 'law_and_political_science'
ENVIRONMENTAL_SCIENCES = 'environmental_science'


PROFESSION_KEYWORDS = {
    DESIGN: ['dise' + ACCENT_N_PATTERN + 'o', 'dise' + ACCENT_N_PATTERN + 'ador', 'fotografia', 'dise' + ACCENT_N_PATTERN + 'adora'],
    ARTS: ['arte'],
    ENGINEERING: ['ingenieria', 'ingeniero', 'ingeniera', 'backend', 'frontend', 'SQL', 'programador', 'software', 'hardware', 'planos'],
    TECHNICAL_TRADES: ['serigrafia', 'serigrafica'],
    ARCHITECTURE: ['arquitectura', 'urbano'],
    BUSINESS: ['administracion', 'administrador', 'economia', 'administrativo', 'administrativa', 'finanzas', 'financiero', 'MBA'],
    SCIENCE: ['investigacion', 'biologia', 'fisica', 'quimica'],
    MARKETING: ['marketing', 'mercadeo'],
    SOCIAL_SCIENCE: ['ciencias sociales', 'investigacion', 'cultura', 'docencia', 'sociales', 'historico', 'investigadora', 'museo'],
    HEALTH_SCIENCES: ['ciencias de la salud', 'enfermedad', 'medicos?', 'cirugia', 'quirurgico', 'salud ocupacional', 'emergencias'],
    PSYCHOLOGY: ['psicologia', 'talento humano', 'recursos humanos', 'seleccion de personal'],
    COMMUNICATION: ['comunicacion', 'audiovisual', 'tv', 'comunicacion social', 'periodismo', 'periodisticas', 'periodistica', 'comunicacion organizacional', 'television'],
    LAW_AND_POLITICAL_SCIENCE: ['derecho', 'politica'],
    ENVIRONMENTAL_SCIENCES: ['ambiente'],
    OPERATOR: ['atencion al cliente']
}

PROFESSIONS = [DESIGN,
               ENGINEERING,
               TECHNICAL_TRADES,
               ARCHITECTURE,
               BUSINESS,
               SCIENCE,
               MARKETING,
               SOCIAL_SCIENCE,
               HEALTH_SCIENCES,
               PSYCHOLOGY,
               COMMUNICATION,
               LAW_AND_POLITICAL_SCIENCE,
               ENVIRONMENTAL_SCIENCES,
               ARTS, ]


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

        new_idx = max(EDUCATION[level] - (total < -1), 0)

        # to be undergrad or more at least be MIN_UNDERGRAD_AGE.
        if new_idx >= EDUCATION[UNDERGRADUATE] and self.age is not None and self.age < MIN_UNDERGRAD_AGE:
            age_undergrad_score = 1
        else:
            age_undergrad_score = 0

        # to be technical or more at least be MIN_TECHNICAL_AGE.
        if new_idx >= EDUCATION[TECHNICAL] and self.age is not None and self.age < MIN_TECHNICAL_AGE:
            age_technical_score = 1
        else:
            age_technical_score = 0

        return new_idx - age_undergrad_score - age_technical_score

    def get_education(self, text):

        levels_score = dict()

        for level, patterns in EDUCATION_KEYWORDS.items():

            # the level itself is a pattern
            patterns = [e for e in patterns] + [level]

            results = [len(re.findall(p, text, re.IGNORECASE)) for p in patterns]

            levels_score[level] = (sum(results) > 0) * EDUCATION[level]

        level = max(levels_score.items(), key=operator.itemgetter(1))[0]

        level_number = self.downgrade_if_not_completed(text, level)

        level_names = list(EDUCATION.keys())

        return level_names[level_number]

    @staticmethod
    def get_city(text):
        return 'la'  # TODO: implement

    def get_experience(self, text):

        preparing_years = EDUCATION_DURATIONS[HIGH_SCHOOL]

        if self.education_level == TECHNICAL:
            preparing_years += EDUCATION_DURATIONS[TECHNICAL]

        if self.education_level == UNDERGRADUATE:
            preparing_years += EDUCATION_DURATIONS[UNDERGRADUATE]

        if self.education_level == MASTER:
            preparing_years += EDUCATION_DURATIONS[UNDERGRADUATE] + EDUCATION_DURATIONS[MASTER]

        if self.education_level == PHD:
            preparing_years += EDUCATION_DURATIONS[UNDERGRADUATE] + \
                               EDUCATION_DURATIONS[MASTER] + \
                               EDUCATION_DURATIONS[PHD]

        if self.age is not None:
            return (self.age - preparing_years)*0.56  # Empirically found the occupation rate to be 56%.
        else:
            return None

    def get_age(self, text):
        """Tries in this order:
            1. Getting the explicit age (eg. Edad: 26 años)
            2. Getting the birth date (eg nacimiento: 19 de Mayo de 1980)
            3. Infer age from time the subject started college and add 18 years.
            4. Infer age when the user finished college and add 5 years for undergrad and 3 years to technical, plus 18
        """

        explicit_age = age_module.find_explicit_age(text)

        if explicit_age is None:
            birth_date = age_module.find_birth_date(text)
            if birth_date is not None:
                return age_module.age_given_birth(birth_date)
            else:
                return age_module.get_college_starting_age(text)
        else:
            return explicit_age

    def find_highest_scoring_profession(self, score_dict):

        max_key_value = max(score_dict.items(), key=operator.itemgetter(1))

        # 1 match maybe luck on operators case with no education:
        #if max_key_value[1] == 1 and self.education_level == HIGH_SCHOOL:
        #    return OPERATOR

        if max_key_value[1] > 0:
            return max_key_value[0]
        else:
            return OPERATOR

    @staticmethod
    def transform_to_pattern(keyword):
        return '(?:(?![a-z]).|^|\n)' + keyword + '(?:(?![a-z]).|$|\n)'

    def get_profession(self, text):

        score_dict = {}
        for profession, keywords in PROFESSION_KEYWORDS.items():
            count = [len(re.findall(self.transform_to_pattern(keyword), text, re.IGNORECASE)) for keyword in keywords]
            total_sum = sum(count)
            opportunities = len(keywords)  # opportunities of doing a match, or number of keywords. This is statistics!
            #score = total_sum/opportunities
            score = total_sum
            score_dict[profession] = score

        return self.find_highest_scoring_profession(score_dict)

    def set_attribute(self, value, text, attribute_name):

        if value is None:
            method_to_call = getattr(self, 'get_' + attribute_name)
            value = method_to_call(text)

        setattr(self, attribute_name, value)

    def __init__(self, text, country=None, institutions=(), education=None, city=None, experience=None, age=None,
                 profession=None):
        self.text = text

        self.set_attribute(age, text, 'age')
        self.set_attribute(country, text, 'country')
        self.set_attribute(city, text, 'city')
        self.set_attribute(institutions, text, 'institutions')
        self.set_attribute(education, text, 'education')
        self.set_attribute(experience, text, 'experience')
        self.set_attribute(profession, text, 'profession')
