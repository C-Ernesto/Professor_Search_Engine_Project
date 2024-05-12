from WebCrawler import WebCrawler
from Index import Index
from Parser import parser

def main():
    # Step 1: Crawl the web (called only once)
    #crawler = WebCrawler("https://www.cpp.edu/engineering/ce/index.shtml")
    #crawler.start_crawler()

    # Step 2: Parse crawled data (called only once)
    docsDict = parser()

    # Step 3: Create index (called only once)
    index = Index(docsDict)
    index.start_indexing()

    while True:
        # Step 4: Take user input for the query
        query = input("Enter your search query (type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        # Step 5: Perform ranking using the Index class method
        ranking = index.getDocumentRanking(query)

if __name__ == "__main__":
    main()