import os
import re
import json

import psycopg2 as pg


def insert_into_db(conn, cur, k, v):

    def prep(sentence):
        regex = "(?<=\w)(?<![\[\s:]u)'(?=\w)"
        sentence = re.sub(regex, "''", sentence)

        regex = '(?<=\w)(?<![\[\s:]u)"(?=\w)'
        sentence = re.sub(regex, '""', sentence)

        return sentence 

    
    title = prep(k)
    arr = prep(','.join(v)).split(',')
    for neighbour in arr:
        cur.execute(f"INSERT INTO wiki_table(title, neighbour) VALUES ('{title}', '{neighbour}')")
    
        conn.commit()

def select_all(cur):
    cur.execute(f"SELECT title, neighbour FROM wiki_table")
    ls = cur.fetchall()

    if len(ls) > 1:
        d = {}
        for k, v in ls:
            if d.get(k) is not None:
                d[k] += [v]
            else:
                d[k] = [v]

        return 1, d

    return 0, ls


if __name__ == '__main__':
    import configparser

    conf = configparser.ConfigParser()
    conf.read('conf.ini')
    
    conn = pg.connect(**conf['DATABASE'])
    cur = conn.cursor()
    
    found, d = select_all(cur)
    if found:
        print(d)