# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 12:26:56 2017

@author: grizzly
"""

import requests, datetime, sqlite3
from bs4 import BeautifulSoup
conn = sqlite3.connect('Base.sqlite')
c = conn.cursor()

class Parser():

    def __init__(self):
        self.key = ''
        self.place = 1
        self.places = []
        self.titles = []
        self.prices = []
        self.links = []
        
    def logging(self, s):
        date = datetime.datetime.now()
        date = date.strftime("%d.%m.%Y %H:%M:%S")
        file = open("log.txt", "a")
        file.write(date + ' - ' + s + '\n')
        file.close()
    

    def write_base(self):
        self.logging('Старт записи в базу данный...')
        data = []
        new_table = False
        date = datetime.datetime.now()
        date = date.strftime("%d.%m.%Y %H:%M:%S")
        try:
            c.execute("CREATE TABLE '%s' (title NOT NULL, place, price, link, date)"% self.key)
            conn.commit()
            new_table = True
            print('New table')
        except sqlite3.OperationalError as e:
            pass
        i = 0
        for title in self.titles:
            data.append((title[1:-2], self.places[i], self.prices[i], self.links[i], date))
            i += 1
        if new_table:
            c.executemany("INSERT INTO {tn} (title,place,price,link,date) VALUES(?, ?, ?, ?, ?);".format(tn=self.key), data)
            conn.commit()
            print('Добавлено - ' + str(len(data)) + ' записей')
            pass
        
        else:
            i = 0
            for lists in data: 
                try:
                    print(lists[0])
                    c.execute('SELECT * FROM {tn} WHERE title = "%s"'.format(tn=self.key) % lists[0])
                    row = c.fetchone()
                    pl = row[1] + '/' + self.places[i]
                    print(pl)
                    c.execute('UPDATE {tn} SET place = "%s" WHERE title = "%s"'.format(tn=self.key) % (pl, lists[0]) )
                    conn.commit()
                    i += 1
                except TypeError:
                    c.execute("INSERT INTO {tn} (title,place,price,link,date) VALUES(?, ?, ?, ?, ?);".format(tn=self.key), lists)
                    conn.commit()
            pass
        
        print('Запись в базу данных успешна.')
        
        self.logging('Запись в базу данных успешна.')
        
    
    
    
    # Получение кода страницы (Адрес страницы)
    def getHtml(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'}
            page = requests.get(url, headers=headers)
            html = page.text
            return html
        except Exception as ex:
            self.logging('ERROR: ' + str(ex))
            raise ex
    
    
    
    
    # Парсинг (Страница поиска амазона, минимальная цена, максимальная цена)
    def parse(self, html, price_min=0.10, price_max=5):
        try:
            soup = BeautifulSoup(html, "lxml")
            titles = []
            prices = []
            t = []
            p1 = []
            p2 = [] 
            links = []
            
            for row in soup.find_all('li', class_= 's-result-item celwidget '):
                t.append(row.find_all('h2'))
                lk = row.find_all('a', class_='a-size-small a-link-normal a-text-normal')
                lk = str(lk)
                i1 = lk.find('https')
                i2 = lk.find('">Kindle Edition</a>')
                links.append(lk[i1:i2])           
                
            for e in t:
                e = str(e)
                ind = e.find('data-max-rows')
                titles.append(e[80:ind])
            
            for row in soup.find_all('span', class_= 'sx-price-whole'):
                row = str(row)[29:-7]
                p1.append(row)
            for row in soup.find_all('sup', class_= 'sx-price-fractional'):
                row = str(row)[33:-6]
                p2.append(row)
            i = 0
            for p in p1:
                prices.append(float(p + '.' + p2[i]))
                i+=1
            i = 0
            for e in prices:
                if e > price_min and e < price_max:
                    self.titles.append(titles[i])
                    self.prices.append(str(e))
                    self.places.append(str(self.place))
                    self.links.append(links[i])
                    print()
                    print(titles[i] + 'цена - ' + str(e) + ' место - ' + str(self.place))
                    print()
                    #print(links[i])
                i+=1
                self.place += 1
            
        except Exception as ex:
            self.logging('ERROR: ' + str(ex))
            raise ex
    
    
    # Запуск парсинга определенного количества страниц(Количество страниц, ключевик)
    def start_parsing(self, pages=10, key='nonfiction'):
        self.place = 1
        self.places = []
        self.titles = []
        self.prices = []
        self.links = []
        self.key = key
        self.logging('Начало парсинга ' + str(pages) + ' страниц...' )

        link = 'https://www.amazon.com/s/ref=sr_pg_1?fst=as%3Aoff&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A157325011%2Ck%3Anonfiction%2Cp_n_date%3A1249100011&sort=relevancerank&keywords=' + key + '&ie=UTF8&qid=1506592543'
        self.parse(self.getHtml(link))
        self.logging('Парсинг первой страницы прошел успешно')
        print('Парсинг первой страницы прошел успешно')
        i = 2
        for e in range(pages - 1):
            link = 'https://www.amazon.com/s/ref=sr_pg_' + str(i) + '?fst=as%3Aoff&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A157325011%2Ck%3Anonfiction%2Cp_n_date%3A1249100011&page=' + str(i) + '&sort=relevancerank&keywords=' + key + '&ie=UTF8&qid=1506593354'
            self.parse(self.getHtml(link))
            self.logging('Парсинг ' + str(i) + ' страницы прошел успешно')
            print('Парсинг ' + str(i) + ' страницы прошел успешно')
            i += 1
        self.write_base()


if __name__ == '__main__':
    parser = Parser()
    parser.start_parsing(10)
    #parser.key = 'nonfiction'
    #parser.write_base()
    c.close()
    conn.close()
