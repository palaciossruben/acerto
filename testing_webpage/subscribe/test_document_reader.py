import unittest

from user import *
from document_reader import read_all

TEST_VALUES = {'1': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25, experience=2, profession=DESIGN),
               '10': User('', country=MEXICO, education_level=UNDERGRADUATE, age=23, experience=3, profession=[MARKETING, DESIGN]),
               '11': User('', country=PERU, education_level=TECHNICAL, age=24, experience=5, profession=OPERATOR),
               '12': User('', country=VENEZUELA, education_level=UNDERGRADUATE, age=29, experience=6, profession=DESIGN),
               '13': User('', country=VENEZUELA, education_level=UNDERGRADUATE, age=36, experience=12, profession=ENGINEERING),
               '14': User('', country=COLOMBIA, education_level=TECHNICAL, age=21, experience=2, profession=ENGINEERING),
               '15': User('', country=COLOMBIA, education_level=TECHNICAL, age=22, experience=1, profession=COMMUNICATION),
               '16': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=24, experience=1, profession=ARCHITECTURE),
               '17': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=29, experience=7, profession=BUSINESS),
               '19': User('', country=CHILE, education_level=HIGH_SCHOOL, age=52, experience=10, profession=OPERATOR),
               '2': User('', country=COLOMBIA, education_level=MASTER, age=30, experience=5, profession=SCIENCE),
               '20': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25, experience=3, profession=MARKETING),
               '21': User('', country=ECUADOR, education_level=HIGH_SCHOOL, age=None, experience=3, profession=OPERATOR),
               '22': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=26, experience=1.67, profession=BUSINESS),
               '23': User('', country=ECUADOR, education_level=MASTER, age=28, experience=3.5, profession=[SOCIAL_SCIENCE, COMMUNICATION]),
               '24': User('', country=COLOMBIA, education_level=TECHNICAL, age=21, experience=0, profession=ENGINEERING),
               '25': User('', country=COLOMBIA, education_level=TECHNICAL, age=23, experience=2.33, profession=BUSINESS),
               '26': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=28, experience=2.83, profession=HEALTH_SCIENCES),
               '27': User('', country=COLOMBIA, education_level=HIGH_SCHOOL, age=19, experience=0.33, profession=TECHNICAL_TRADES),
               '28': User('', country=PERU, education_level=UNDERGRADUATE, age=32, experience=6.67, profession=PSYCHOLOGY),
               '29': User('', country=PERU, education_level=UNDERGRADUATE, age=23, experience=3.25, profession=COMMUNICATION),
               '3': User('', country=COLOMBIA, education_level=TECHNICAL, age=31, experience=7, profession=BUSINESS),
               '30': User('', country=ECUADOR, education_level=TECHNICAL, age=24, experience=None, profession=OPERATOR),
               '31': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=22, experience=0, profession=DESIGN),
               '32': User('', country=ECUADOR, education_level=TECHNICAL, age=21, experience=0.67, profession=PSYCHOLOGY),
               '33': User('', country=COLOMBIA, education_level=TECHNICAL, age=22, experience=2, profession=DESIGN),
               '34': User('', country=COLOMBIA, education_level=TECHNICAL, age=20, experience=12, profession=[ENGINEERING, COMMUNICATION]),
               '35': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=26, experience=1.67, profession=[MARKETING, DESIGN]),
               '36': User('', country=PERU, education_level=TECHNICAL, age=53, experience=22.41, profession=BUSINESS),
               '37': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25, experience=5, profession=SOCIAL_SCIENCE),
               '38': User('', country=COLOMBIA, education_level=TECHNICAL, age=20, experience=1.08, profession=LAW_AND_POLITICAL_SCIENCE),
               '39': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=32, experience=0, profession=DESIGN),
               '4': User('', country=COLOMBIA, education_level=MASTER, age=55, experience=31, profession=BUSINESS),
               '41': User('', country=CHILE, education_level=TECHNICAL, age=33, experience=7.25, profession=HEALTH_SCIENCES),
               '45': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=25, experience=5, profession=SOCIAL_SCIENCE),
               '46': User('', country=COLOMBIA, education_level=MASTER, age=31, experience=7.17, profession=BUSINESS),
               '48': User('', country=BOLIVIA, education_level=MASTER, age=26, experience=0.75, profession=BUSINESS),
               '49': User('', country=ECUADOR, education_level=HIGH_SCHOOL, age=21, experience=2, profession=OPERATOR),
               '5': User('', country=COLOMBIA, education_level=TECHNICAL, age=26, experience=1.58, profession=ENVIRONMENTAL_SCIENCES),
               '50': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=27, experience=4, profession=COMMUNICATION),
               '51': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=24, experience=4.5, profession=COMMUNICATION),
               '52': User('', country=COLOMBIA, education_level=TECHNICAL, age=21, experience=1.33, profession=ENGINEERING),
               '53': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=29, experience=6, profession=HEALTH_SCIENCES),
               '54': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=26, experience=1.5, profession=PSYCHOLOGY),
               '55': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=34, experience=2.5, profession=DESIGN),
               '56': User('', country=COLOMBIA, education_level=TECHNICAL, age=22, experience=9, profession=ARTS),
               '57': User('', country=CHILE, education_level=UNDERGRADUATE, age=24, experience=5.5, profession=COMMUNICATION),
               '58': User('', country=PERU, education_level=HIGH_SCHOOL, age=27, experience=7.5, profession=DESIGN),
               '59': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=35, experience=10.3, profession=ENGINEERING),
               '6': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=26, experience=6, profession=DESIGN),
               '60': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=29, experience=5.33, profession=ENGINEERING),
               '61': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25, experience=1.16, profession=ENGINEERING),
               '62': User('', country=ARGENTINA, education_level=UNDERGRADUATE, age=29, experience=9, profession=COMMUNICATION),
               '63': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=23, experience=1.91, profession=SOCIAL_SCIENCE),
               '64': User('', country=COLOMBIA, education_level=TECHNICAL, age=28, experience=3.83, profession=PSYCHOLOGY),
               '65': User('', country=COLOMBIA, education_level=TECHNICAL, age=23, experience=None, profession=DESIGN),
               '7': User('', country=COLOMBIA, education_level=HIGH_SCHOOL, age=18, experience=0, profession=MARKETING),
               }


def accuracy(y, y_prediction):
    return sum([e_y == e_ypred for e_y, e_ypred in zip(y, y_prediction)]) / len(y)


# The profession can be more than 1, Will be OK if it has at least one of the answers right
# Be careful with:
# >>> ['art', 'engineering'] in ['art', 'engineering']
# False
def profession_accuracy(y, y_prediction):
    return sum([e_ypred in e_y for e_y, e_ypred in zip(y, y_prediction)]) / len(y)

RESULTS_DICT = read_all()


class DocumentTest(unittest.TestCase):

    def test_country(self):

        for key, user in TEST_VALUES.items():
            #print('checking country for key: {}'.format(key))
            self.assertEqual(RESULTS_DICT[key].country, user.country)

    def test_education_level(self):

        zipped_y = [(user.education_level, RESULTS_DICT[key].education_level) for key, user in TEST_VALUES.items()]

        y, y_prediction = zip(*zipped_y)

        #results = [str(key) + str(e_y == e_y_prediction) for key, e_y, e_y_prediction in zip(TEST_VALUES.keys(), y, y_prediction)]
        #print('tag: ' + str([key + ' ' + str(e) for key, e, r in zip(TEST_VALUES.keys(), y, results) if 'False' in r]))
        #print('predicted: ' + str([key + ' ' + str(e) for key, e, r in zip(TEST_VALUES.keys(), y_prediction, results) if 'False' in r]))

        a = accuracy(y, y_prediction)

        print('education level accuracy is: ' + str(a))

    @staticmethod
    def avg(array):
        if len(array) > 0:
            return sum(array)/len(array)
        else:
            return None

    def test_age(self):

        unknowns = []
        error = []  # error in years.

        for key, user in TEST_VALUES.items():
            predicted_age = RESULTS_DICT[key].age
            #print('key {} has age: {}'.format(key, predicted_age))

            if predicted_age is not None and user.age is not None:
                current_error = abs(predicted_age - user.age)
                error.append(current_error)
                #print('error is: {}'.format(current_error))
                unknowns.append(0)
            else:  # unknown age.
                unknowns.append(1)

        print('Age % of unknown data: ' + str(self.avg(unknowns)))
        print('Age average error(years): ' + str(self.avg(error)))

    def test_experience(self):

        unknowns = []
        error = []  # error in years.

        for key, user in TEST_VALUES.items():
            predicted_experience = RESULTS_DICT[key].experience
            #print('key {} has experience: {}'.format(key, predicted_experience))

            if predicted_experience is not None and user.experience is not None:
                current_error = abs(predicted_experience - user.experience)
                error.append(current_error)
                #print('error is: {}'.format(current_error))
                unknowns.append(0)
            else:  # unknown age.
                unknowns.append(1)

        print('Experience % of unknown data: ' + str(self.avg(unknowns)))
        print('Experience average error(years): ' + str(self.avg(error)))

    def test_profession(self):

        zipped_y = [(user.profession, RESULTS_DICT[key].profession) for key, user in TEST_VALUES.items()]

        y, y_prediction = zip(*zipped_y)

        results = [str(key) + str(e_y_prediction in e_y) for key, e_y, e_y_prediction in zip(TEST_VALUES.keys(), y, y_prediction)]

        print('tag: ' + str([key + ' ' + str(e) for key, e, r in zip(TEST_VALUES.keys(), y, results) if 'False' in r]))
        print('predicted: ' + str([key + ' ' + str(e) for key, e, r in zip(TEST_VALUES.keys(), y_prediction, results) if 'False' in r]))

        a = profession_accuracy(y, y_prediction)

        print('Profession accuracy is: ' + str(a))

if __name__ == '__main__':
    unittest.main()
