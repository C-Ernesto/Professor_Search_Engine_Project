import string
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import distance

import Index


# nltk.download()

class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]


def connectDataBase():
    # Create a database connection object using pymongo

    DB_NAME = "project"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:

        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]

        return db

    except:
        print("Database not connected successfully")


def getDocumentRanking(vectorizer, tfidf_matrix, query):
    queryText = query

    # remove punctuation
    queryText.translate(str.maketrans('', '', string.punctuation))

    # stopping and stemming
    # vectorizer = CountVectorizer(stop_words='english', tokenizer=LemmaTokenizer())

    # transform query to vector, also performs stopping and stemming
    vector = vectorizer.transform([queryText])
    # print(vectorizer.vocabulary_)
    # print(vector.toarray())

    # get cosine similarity
    cosine_similarity_values = cosine_similarity(tfidf_matrix.toarray(), vector.toarray()).flatten()

    # enumerate and sort to get doc ID of highest similarity
    cosine_enum = list(enumerate(cosine_similarity_values))
    ranking = sorted(cosine_enum, key=lambda x: x[1], reverse=True)
    # print(ranking)

    # get URL for the doc ID
    db = connectDataBase()
    webpage = db.webpage

    count = 1
    for DocID, val in ranking:
        url = webpage.find_one({"_id": DocID})['url']
        print("%d. %s   |   Similarity: %f" % (count, url, val))
        count += 1

    return ranking


if __name__ == '__main__':
    documents = {
        0: "apple",
        1: "banana orange",
        2: "apple orange"
    }

    index = Index.Index(documents)
    index.create_inverted_index()
    vec = index.getTfidfVectorizer()
    count_matrix = index.getTfidfMatrix()
    countQuery = getDocumentRanking(vec, count_matrix, "The apple slept behind the banana")
