import time
from pymongo import MongoClient
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError


class WebCrawler:

    def __init__(self, seed):
        self.frontier = [seed]
        self.visited_links = []

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

    def crawlerThread(self, con, num_targets=10, DEBUG=False):
        targets_found = 0

        while self.frontier:
            # get url
            url = self.frontier.pop(0)
            try:
                if DEBUG:
                    print("Crawling: " + url)
                # get html
                html = urlopen(url)
                bs = BeautifulSoup(html.read(), 'html.parser')

                # check if url is a target page
                if self.target_page(bs, DEBUG):
                    self.store_page(con, url, bs, True)
                    targets_found += 1
                else:
                    self.store_page(con, url, bs, False)

                # add url to visited
                self.visited_links.append(url)

                # check if we reach target number
                if targets_found == num_targets:
                    self.frontier = []
                else:
                    # add all urls
                    links = bs.find_all('a', href=True)
                    for link in links:
                        resource = link.get('href')
                        # join url
                        completeURL = urljoin("https://www.cpp.edu/", resource)
                        # add url to frontier
                        if completeURL not in self.visited_links and completeURL not in self.frontier:
                            self.frontier.append(completeURL)

            except HTTPError as e:
                if DEBUG:
                    print(e)
            except Exception as e:
                if DEBUG:
                    print(e)

    def target_page(self, bs, DEBUG=False):
        # return true if target page
        try:
            header = bs.find('div', {'class': 'row'})
            info = bs.find('div', {'class': 'span10'})
            left = info.find('div', {'class': 'menu-left'})
            email = left.find('p', {'class', 'emailicon'})
            phone = left.find('p', {'class', 'phoneicon'})
            right = info.find('div', {'class': 'menu-right'})
            location = right.find('p', {'class', 'locationicon'})
            hours = right.find('p', {'class', 'hoursicon'})
            return True
        except AttributeError as e:
            if DEBUG:
                print("not target page")
            return False

    def store_page(self, con, url, bs, isTarget: bool):
        page = {
            'url': url,
            'html': str(bs),
            "istarget": isTarget
        }
        con.insert_one(page)

    def start_crawler(self, DEBUG=False):
        db = self.connectDataBase()
        webpage = db.webpage

        self.crawlerThread(webpage, 10, DEBUG)


if __name__ == '__main__':
    start = time.time()
    crawler = WebCrawler("https://www.cpp.edu/engineering/ce/index.shtml")
    crawler.start_crawler(False)
    end = time.time()
    print(end - start)
