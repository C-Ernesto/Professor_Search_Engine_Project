from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient


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


def create_inverted_index(docs):
    # convert documents to list
    corpus = list(docs.values())

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Get terms
    feature_names = vectorizer.get_feature_names_out()

    inverted_index = {}

    # Iterate over terms and documents to build inverted index
    # tfidf_matrix is a 2d array where row = doc_id and col = term
    for i, term in enumerate(feature_names):
        inverted_index[term] = []
        for doc_id, text in docs.items():
            tfidf_matrix_np = tfidf_matrix.toarray()
            tfidf = tfidf_matrix_np[doc_id][i]
            # only consider non-zero terms
            if tfidf > 0:
                inverted_index[term].append({
                    "doc_id": doc_id,
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

    # inverted_index = create_inverted_index(documents)
    #
    # # Print inverted index
    # for term, postings in inverted_index.items():
    #     print(term + ":")
    #     for posting in postings:
    #         print(f"   Doc ID: {posting['doc_id']}, TF-IDF: {posting['tfidf']:.4f}")
