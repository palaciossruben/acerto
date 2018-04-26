from nltk.stem.snowball import SnowballStemmer

print(" ".join(SnowballStemmer.languages))

stemmer = SnowballStemmer("english")

print(stemmer.stem("running"))

stemmer2 = SnowballStemmer("english", ignore_stopwords=True)
print(stemmer.stem("having"))
print(stemmer2.stem("having"))

print(SnowballStemmer("english").stem("generously"))
print(SnowballStemmer("porter").stem("generously"))

stemmer_spa = SnowballStemmer("spanish", ignore_stopwords=True)
print(stemmer_spa.stem("generosamente"))
