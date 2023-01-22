from typing import List

import requests
from requests.exceptions import RequestException

from bs4 import BeautifulSoup
import time
import json
import os

import psycopg2 as pg


from my_tools import select_all, insert_into_db

requests_per_minute = 100
links_per_page = 200

main_body = r'https://uk.wikipedia.org/wiki/'


import configparser


conf = configparser.ConfigParser()
conf.read('conf.ini')


class WikiRacer:
    def __init__(self, max_depth = 4):
        self.temp = []
        self.__max_depth = max_depth
        self.__depth_reached = False
        self._path = {}
        self._d = {}
        self.last_call = None

        self.conn = pg.connect(**(conf["DATABASE"]))
        self.cur = self.conn.cursor()

        found, d = select_all(self.cur) 
        if found:
            self._d = d

    def change_maxdepth(self, depth) -> None:
        self.__max_depth = depth
        

    def limiter(self, max_per_min):
        if self.last_call is None:
            return 0

        interval = 60. / float(max_per_min)

        differ = time.time() - self.last_call
        wait_time = interval - differ

        return wait_time




    @staticmethod
    def finished(d, finish):
        if d.get(finish) is not None:
            return 1
        else:
            return 0

    
    def filter_links(self, links) -> List[str]:
        ls = []
        accepted_class = [None, 'mw-redirect']
        check_none = lambda c: c if c is None else ' '.join(c)


        for link in links:
            link_check = link['href'].startswith('/wiki')
            text_check = link.text != ''
            title_check = link.get('title') is not None
            class_check = check_none(link.get('class')) in accepted_class
            previous_check = link.get('title') not in self._path.keys()\
             and link.get('title') not in ls 

            accepted = link_check and text_check and title_check and class_check\
                        and previous_check


            if accepted:
                # print(link['href'])
                ls.append(link['title'])
 
        return ls[:links_per_page]

    def track_path(self, cols, link) -> None:
        if len(self._path) == 0:
            for col in cols:
                self._path[col] = [link] + [col]
        else:
            for col in cols:

                if len(self._path[link] + [col]) > self.__max_depth:
                    
                    self.__depth_reached = True

                    break
                else:            
                    self._path[col] = self._path[link] + [col]


    def find_neighbours(self, link):

        # code for hashed data
        if self._d.get(link) is not None:
            self.temp += self._d[link]

            # track paths into our dictionary of paths
            ls = self._d[link]

            self.track_path(ls, link)


        else:
            # rate limiting
            wait_time = self.limiter(requests_per_minute)
            if wait_time > 0:
                time.sleep(wait_time)

            retry_counter = 0

            while True:
                try:
                    r = requests.get(main_body + link)
            
                    if r.status_code == 404:
                        return None

                    break
                except RequestException as e:
                        time.sleep(60./requests_per_minute)
                        # print('yes')
                        if retry_counter > 3:
                            return None


                        retry_counter += 1


            bs = BeautifulSoup(r.content, 'lxml')
            div = bs.find('div', attrs={'id': 'mw-content-text'})

            ls = self.filter_links(div.find_all('a', href=True))
            
            
            # adding our new links from this node to queue
            if len(ls) > 0:
                self.temp += ls
                insert_into_db(self.conn, self.cur, link, ls)
                self._d[link] = ls
                

                # track paths into our dictionary of paths
                self.track_path(ls, link)
                    

        

    def find_path(self, start: str, finish: str) -> List[str]:

        # check whether there is path to finish in current dictionary of paths 
        while not self.finished(self._path, finish):
            self.find_neighbours(start)
            if self.__depth_reached:
                break

            self.last_call = time.time()
            
            try:
                start = self.temp.pop(0)
            except Exception as e:
                # print(e)
                return []

        with open('my_json.json', 'w') as f:
            json.dump(self._d, f)

        if self.__depth_reached and self._path.get('finish') is None:
            result = []
            self.__depth_reacher = False
        else:
            result = self._path[finish]

        self._path = {}
        self.temp = []

        return result



        

if __name__ == '__main__':
    start = time.time()
    racer = WikiRacer(max_depth=4)

    path = racer.find_path('Дружба', 'Париж')

    print(path)
    spent = time.time() - start
    print(spent)    