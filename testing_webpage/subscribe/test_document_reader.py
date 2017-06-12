import unittest

from user import *
from document_reader import read_all

TEST_VALUES = {'1': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25, experience=2),
               '10': User('', country=MEXICO, education_level=UNDERGRADUATE, age=23, experience=3),
               '11': User('', country=PERU, education_level=TECHNICAL, age=24, experience=5),
               '12': User('', country=VENEZUELA, education_level=UNDERGRADUATE, age=29, experience=6),
               '13': User('', country=VENEZUELA, education_level=UNDERGRADUATE, age=36, experience=12),
               '14': User('', country=COLOMBIA, education_level=TECHNICAL, age=21, experience=2),
               '15': User('', country=COLOMBIA, education_level=TECHNICAL, age=22, experience=1),
               '16': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=24, experience=1),
               '17': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=29, experience=7),
               '19': User('', country=CHILE, education_level=HIGH_SCHOOL, age=52),
               '2': User('', country=COLOMBIA, education_level=MASTER, age=30),
               '20': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25),
               '21': User('', country=ECUADOR, education_level=TECHNICAL, age=None),
               '22': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=26),
               '23': User('', country=ECUADOR, education_level=MASTER, age=28),
               '24': User('', country=COLOMBIA, education_level=TECHNICAL, age=21),
               '25': User('', country=COLOMBIA, education_level=TECHNICAL, age=23),
               '26': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=28),
               '27': User('', country=COLOMBIA, education_level=HIGH_SCHOOL, age=19),
               '28': User('', country=PERU, education_level=UNDERGRADUATE, age=32),
               '29': User('', country=PERU, education_level=UNDERGRADUATE, age=23),
               '3': User('', country=COLOMBIA, education_level=TECHNICAL, age=31),
               '30': User('', country=ECUADOR, education_level=TECHNICAL, age=24),
               '31': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=22),
               '32': User('', country=ECUADOR, education_level=TECHNICAL, age=21),
               '33': User('', country=COLOMBIA, education_level=TECHNICAL, age=22),
               '34': User('', country=COLOMBIA, education_level=TECHNICAL, age=20),
               '35': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=26),
               '36': User('', country=PERU, education_level=TECHNICAL, age=53),
               '37': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25),
               '38': User('', country=COLOMBIA, education_level=TECHNICAL, age=20),
               '39': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=32),
               '4': User('', country=COLOMBIA, education_level=MASTER, age=55),
               '41': User('', country=CHILE, education_level=TECHNICAL, age=33),
               '45': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=25),
               '46': User('', country=COLOMBIA, education_level=MASTER, age=31),
               '48': User('', country=BOLIVIA, education_level=MASTER, age=26),
               '49': User('', country=ECUADOR, education_level=HIGH_SCHOOL, age=21),
               '5': User('', country=COLOMBIA, education_level=TECHNICAL, age=26),
               '50': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=27),
               '51': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=24),
               '52': User('', country=COLOMBIA, education_level=TECHNICAL, age=21),
               '53': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=29),
               '54': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=26),
               '55': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=34),
               '56': User('', country=COLOMBIA, education_level=TECHNICAL, age=22),
               '57': User('', country=CHILE, education_level=UNDERGRADUATE, age=24),
               '58': User('', country=PERU, education_level=HIGH_SCHOOL, age=27),
               '59': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=35),
               '6': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=26),
               '60': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=29),
               '61': User('', country=COLOMBIA, education_level=UNDERGRADUATE, age=25),
               '62': User('', country=ARGENTINA, education_level=UNDERGRADUATE, age=29),
               '63': User('', country=ECUADOR, education_level=UNDERGRADUATE, age=23),
               '64': User('', country=COLOMBIA, education_level=TECHNICAL, age=28),
               '65': User('', country=COLOMBIA, education_level=TECHNICAL, age=23),
               '7': User('', country=COLOMBIA, education_level=HIGH_SCHOOL, age=18),
               }


def accuracy(y, y_prediction):
    return sum([e_y == e_ypred for e_y, e_ypred in zip(y, y_prediction)]) / len(y)


RESULTS_DICT = read_all()


class DocumentTest(unittest.TestCase):

    def test_country(self):

        for key, user in TEST_VALUES.items():
            #print('checking country for key: {}'.format(key))
            self.assertEqual(RESULTS_DICT[key].country, user.country)

    def test_education_level(self):

        zipped_y = [(user.education_level, RESULTS_DICT[key].education_level) for key, user in TEST_VALUES.items()]

        y, y_prediction = zip(*zipped_y)

        results = [str(key) + str(e_y == e_y_prediction) for key, e_y, e_y_prediction in zip(TEST_VALUES.keys(), y, y_prediction)]
        negatives = [e for e in results if 'False' in e]
        #print(negatives)
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

        print('% of unknown data: ' + str(self.avg(unknowns)))
        print('average error(years): ' + str(self.avg(error)))


if __name__ == '__main__':
    unittest.main()
