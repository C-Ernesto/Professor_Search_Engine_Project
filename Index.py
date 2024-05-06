from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from pymongo import MongoClient
from collections import OrderedDict

class Index:

    def __init__(self, docsDict):
        self.docsDict = docsDict
        self.countVectorizer = CountVectorizer()
        self.tfidfVectorizer = TfidfVectorizer()
        self.count_matrix = []
        self.tfidf_matrix = []
        self.inverted_index = {}

    def getCountVectorizer(self):
        return self.countVectorizer

    def getTfidfVectorizer(self):
        return self.tfidfVectorizer

    def getInvertedIndex(self):
        return self.inverted_index.copy()

    def getCountMatrix(self):
        return self.count_matrix.copy()

    def getTfidfMatrix(self):
        return self.tfidf_matrix.copy()

    def connectDataBase(self):
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


    def create_inverted_index(self):

        # convert docs to ordered dict
        docs = OrderedDict(self.docsDict)

        # convert documents to list
        corpus = list(docs.values())

        # Create a CountVectorizer to get word counts
        # countVectorizer = CountVectorizer()
        self.count_matrix = self.countVectorizer.fit_transform(corpus)
        count_matrix_np = self.count_matrix.toarray()

        # Create TF-IDF vectorizer
        # tfidfVectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.tfidfVectorizer.fit_transform(corpus)
        tfidf_matrix_np = self.tfidf_matrix.toarray()

        # Get terms
        feature_names = self.tfidfVectorizer.get_feature_names_out()

        # inverted_index = {}

        # Iterate over terms and documents to build inverted index
        # tfidf_matrix is a 2d array where row = doc_id and col = term
        for i, term in enumerate(feature_names):
            self.inverted_index[term] = []
            for doc_id, text in docs.items():
                tfidf = tfidf_matrix_np[doc_id][i]
                count = count_matrix_np[doc_id][i].item()
                # only consider non-zero terms
                if tfidf > 0:
                    self.inverted_index[term].append({
                        "doc_id": doc_id,
                        "count": count,
                        "tfidf": tfidf
                    })

        # print(inverted_index)

        # convert dictionary to a list
        inverted_index_document = []
        for term, docs in self.inverted_index.items():
            inverted_index_document.append({
                "term": term,
                "documents": docs
            })

        # print(inverted_index_document)

        return inverted_index_document


    def start_indexing(self):
        db = self.connectDataBase()
        index = db.index

        inverted_index = self.create_inverted_index()

        # store inverted index
        index.insert_many(inverted_index)


if __name__ == '__main__':
    # Example input
    documents = {
        0: "apple",
        1: "banana orange",
        2: "apple orange"
    }

    index = Index(documents)
    index.start_indexing()

    #start_indexing(documents)
