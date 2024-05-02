from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from pymongo import MongoClient
from collections import OrderedDict


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


def create_inverted_index(docsDict):

    # convert docs to ordered dict
    docs = OrderedDict(docsDict)

    # convert documents to list
    corpus = list(docs.values())

    # Create a CountVectorizer to get word counts
    countVectorizer = CountVectorizer()
    count_matrix = countVectorizer.fit_transform(corpus)
    count_matrix_np = count_matrix.toarray()

    # Create TF-IDF vectorizer
    tfidfVectorizer = TfidfVectorizer()
    tfidf_matrix = tfidfVectorizer.fit_transform(corpus)
    tfidf_matrix_np = tfidf_matrix.toarray()

    # Get terms
    feature_names = tfidfVectorizer.get_feature_names_out()

    inverted_index = {}

    # Iterate over terms and documents to build inverted index
    # tfidf_matrix is a 2d array where row = doc_id and col = term
    for i, term in enumerate(feature_names):
        inverted_index[term] = []
        for doc_id, text in docs.items():
            tfidf = tfidf_matrix_np[doc_id][i]
            count = count_matrix_np[doc_id][i].item()
            # only consider non-zero terms
            if tfidf > 0:
                inverted_index[term].append({
                    "doc_id": doc_id,
                    "count": count,
                    "tfidf": tfidf
                })

    # print(inverted_index)

    # convert dictionary to a list
    inverted_index_document = []
    for term, docs in inverted_index.items():
        inverted_index_document.append({
            "term": term,
            "documents": docs
        })

    # print(inverted_index_document)

    return inverted_index_document


def start_indexing(docs):
    db = connectDataBase()
    index = db.index

    inverted_index = create_inverted_index(docs)

    # store inverted index
    index.insert_many(inverted_index)


if __name__ == '__main__':
    # Example input
    documents = {
        0: "apple",
        1: "banana orange",
        2: "apple orange"
    }

    start_indexing(documents)
