import string
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from pymongo import MongoClient
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# nltk.download()


class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]


class Index:

    def __init__(self, docsDict):
        self.docsDict = docsDict
        self.countVectorizer = CountVectorizer(stop_words='english', tokenizer=LemmaTokenizer(), ngram_range=(1, 5))
        self.tfidfVectorizer = TfidfVectorizer(stop_words='english', tokenizer=LemmaTokenizer(), ngram_range=(1, 5))
        self.count_matrix = []
        self.tfidf_matrix = []
        self.inverted_index = {}
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

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

        # preprocess text
        # preprocessed_docs = {doc_id: self.preprocess_text(doc_text) for doc_id, doc_text in self.docsDict.items()}

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

    def preprocess_text(self, text):
        tokens = nltk.word_tokenize(text)
        filtered_tokens = [token for token in tokens if token.lower() not in self.stop_words]
        stemmed_tokens = [self.stemmer.stem(token) for token in filtered_tokens]
        preprocessed_text = ' '.join(stemmed_tokens)
        return preprocessed_text

    def start_indexing(self):
        db = self.connectDataBase()
        index = db.index

        inverted_index = self.create_inverted_index()

        # store inverted index
        index.insert_many(inverted_index)

    def printIndex(self):
        for key, val in self.inverted_index.items():
            print(key, ":", val)

    def getDocumentRanking(self, query):
        queryText = query

        # remove punctuation
        queryText = queryText.translate(str.maketrans('', '', string.punctuation))

        # transform query to vector, also performs stopping and stemming
        vector = self.tfidfVectorizer.transform([queryText])
        # print(vectorizer.vocabulary_)
        # print(vector.toarray())

        # get cosine similarity
        cosine_similarity_values = cosine_similarity(self.tfidf_matrix.toarray(), vector.toarray()).flatten()

        # enumerate and sort to get doc ID of highest similarity
        cosine_enum = list(enumerate(cosine_similarity_values))
        ranking = sorted(cosine_enum, key=lambda x: x[1], reverse=True)
        # print(ranking)

        # get URL for the doc ID
        db = self.connectDataBase()
        webpage = db.webpage

        count = 1
        num = 1
        for DocID, val in ranking:
            # truncate at similarity = 0
            if val == 0:
                break

            url = webpage.find_one({"_id": DocID})['url']

            print("%d. %-40s  |  Similarity: %f" % (num, url, val))
            if count == 5:
                cmd = input("Enter n for next page, enter anything else to run another query: ")
                if cmd.lower() == 'n':
                    count = 0
                else:
                    break
            count += 1
            num += 1

        # add line break
        print("\n" + "--------------------------------" * 3 + "\n")

        return ranking


if __name__ == '__main__':
    # Example input
    documents = {
        0: "apple",
        1: "banana orange",
        2: "apple orange"
    }

    index = Index(documents)
    index.start_indexing()
    index.printIndex()
    index.getDocumentRanking("The apples, slept behind the bananas.")
