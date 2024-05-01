from bs4 import BeautifulSoup
from pymongo import MongoClient

def format_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Iterate over all elements in the parsed HTML
    for element in soup.find_all('a'):
        # Replace each hyperlink with its text content
        if element.string:
            element.replace_with(element.string)

    # Return the formatted HTML as a string
    return str(soup)

def parser():
    dict = {}
    # Connect to database
    client = MongoClient("localhost", 27017)
    db = client["project"]
    collection = db["webpage"]

    # Iterate through documents
    for document in collection.find():
        text = ""
        # Get the _id of the document
        doc_id = document['_id']
        # Initialize an empty list for the doc_id if it's in the dictionary
        if doc_id not in dict:
            dict[doc_id] = []
        # Analyze html content from collected target pages
        html_content = format_html(document['html'])
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract information with class "accolades", which contains "Areas of Search"
        accolades_divs = soup.find_all('div', class_='accolades')
        if accolades_divs:
            for accolades_div in accolades_divs:
                # Replace '\n' with space ' '
                text += accolades_div.get_text(separator=' ', strip=True)
        dict[doc_id].append({doc_id: text})
    print(dict)

if __name__ == "__main__":
    parser()
