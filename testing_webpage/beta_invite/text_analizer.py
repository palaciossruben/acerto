import os
import math
import nltk



def my_sigmoid(num_words, num_for_80_percent):
    """
    Gives a score with a sigmoid function increasing with the number of words.
    Has a number of words for which the score is going to be 80%.
    Args:
        num_words: actual number of words
        num_for_80_percent: Number of words to have an score of 80%
    Returns: score.
    """
    # Finds k, by solving the equation 0.8 = 1/(1 + math.exp(num_for_80_percent*k))*2 - 1
    k = math.log(1/0.9-1)/num_for_80_percent
    return 1/(1 + math.exp(num_words * k)) * 2 - 1


def handle_division_by_zero(numerator, denominator):
    """Handles division by zero"""
    return numerator / denominator if denominator > 0 else 0


def get_score(text):
    """
    Score for the text. Has 2 components length and spelling
    Args:
        text: string
    Returns:
    """
    words = [w.lower() for w in nltk.word_tokenize(text)]

    length_score = my_sigmoid(len(words), 15)

    spelling = 0
    with open(os.path.join('subscribe', 'es-MX.dic'), 'r', encoding='UTF-8') as vocabulary_file:

        vocabulary = vocabulary_file.read().split('\n')

        # TODO: add English by un commenting this and adding the english vocabulary

        with open(os.path.join('subscribe', 'en-US.dic'), 'r', encoding='UTF-8') as vocabulary_file_en:
            vocabulary_en = vocabulary_file_en.read().split('\n')

        # TODO: do faster with binary search.
        for w in words:
            # TODO: add English by un commenting this and adding the english vocabulary
            if w in vocabulary or w in vocabulary_en:
                spelling += 1

    spelling_score = handle_division_by_zero(spelling, len(words))

    return length_score * spelling_score
