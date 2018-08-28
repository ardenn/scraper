from bs4 import BeautifulSoup
import csv
import requests
from urllib.request import Request, urlopen
import re
import time
from fake_useragent import UserAgent
import random

class Property24:
    def __init__(self):
        self.title = ""
        self.description = ""
        self.price = ""
        self.location = ""
        self.latitude = ""
        self.longitude = ""
        self.bedrooms = 0
        self.bathrooms = 0
        self.garage_space = 0
        self.parking = ""
        self.garden = ""
        self.category = ""
        self.erf_size = "" 
        self.floor_area = ""
        self.total_floors = 0
        self.list_date = ""
        self.mapscript = ""

class Scraper:
    """docstring for Scraper"""
    def __init__(self):
        self.base_url = 'https://www.property24.co.ke'
        self.filename = 'data3.csv'
        self.user_agent = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
        self.target_file = open(self.filename, "w", newline='',encoding='utf-8')
        self.proxy_url = 'https://www.ssproxies.org/'
        self.ua = UserAgent()    #generate random user agent from here

        self.proxy_random_header = self.ua.random
        
        fieldnames = ['title','description','price','location','latitude','longitude','bedrooms','bathrooms','garage_space',
        'parking','garden','category','erf_size','floor_area','total_floors','list_date','mapscript']

        self.writer = csv.DictWriter(self.target_file, fieldnames=fieldnames)
        self.writer.writeheader()

        
        self.proxies = []        #initiate empty proxy list [ip: port]


    """ Retrieve latest proxies from ssproxies.org """ 
    def retrieveProxies(self):
        soup = BeautifulSoup(
                requests.get(self.proxy_url, params='',headers=self.proxy_random_header).content, 'lxml'
            )
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            self.proxies.append({
                'ip':   row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })

    """ Selects a Random proxy to use from list. Returns index so we can delete proxy if not working """
    def random_proxy(self):
        return random.randint(0, len(self.proxies) - 1)

    def scrape(self,url, headers):

        new_prop = Property24()
        
        t = True
        a = True
        p = True
        d = True


        #choose a random proxy
        proxy_index = self.random_proxy()
        proxy = self.proxies[proxy_index]

        #test proxy before using
        for n in range(1, 100):

            # Every 5 requests, generate a new proxy
            if n % 5 == 0:
                proxy_index = self.random_proxy()
                proxy = self.proxies[proxy_index]

            req = Request(url)
            req.add_header('User-Agent', headers)
            req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')

            # Make the call
            try:
                soup = BeautifulSoup(urlopen(req).read().decode('utf-8'), 'lxml')
                print("Using Proxy : " + proxy['ip'] + ' : Port ' + proxy['port'] + '\n')

                if soup.find('div', class_='sc_listingAddress'):
                    if soup.find('div', class_='sc_listingAddress').find('h1'):
                        new_prop.title = soup.find('div', class_='sc_listingAddress').find('h1').string.strip()
                else:
                    t = False
                if soup.find('div', class_='sc_listingAddress'):
                    if soup.find('div', class_='sc_listingAddress').find('p'):
                        new_prop.location = soup.find('div', class_='sc_listingAddress').find('p').string.strip()
                else:
                    a = False
                if soup.find('div', class_='sc_listingPrice'):
                    if soup.find('div', class_='sc_listingPrice').find('div'):
                        new_prop.price = soup.find('div', class_='sc_listingPrice').find('div').string.strip()
                else:
                    p = False
                if soup.find('div', class_='sc_listingDetailsText'):
                    new_prop.description = soup.find('div', class_='sc_listingDetailsText').get_text()
                else:
                    d = False

                if not t and not a and not p and not d:
                    return

                features = soup.find_all('div', class_='sc_detailsIcon')

                if features and len(features) > 0:
                    for feature in features:
                        if feature.find('img', class_='property24generic_icon_beds_25'):
                            new_prop.bedrooms = feature.find('img',
                                                             class_='property24generic_icon_beds_25').find_next_sibling('span').string.strip()
                        if feature.find('img', class_='property24generic_icon_baths_25'):
                            new_prop.bathrooms = feature.find('img',
                                                              class_='property24generic_icon_baths_25').find_next_sibling('span').string.strip()
                        if feature.find('img', class_='property24generic_icon_parking_25'):
                            if feature.find('img', class_='property24generic_icon_parking_25').find_next_sibling('i', class_='fa-check'):
                                new_prop.parking = "True"

                        if feature.find('img', class_='property24generic_icon_garden_25'):
                            if feature.find('img', class_='property24generic_icon_garden_25').find_next_sibling('i',class_='fa-check'):
                                new_prop.garden = "True"

                        if feature.find('img', class_='property24generic_icon_garages_25'):
                            new_prop.garage_space = int(
                                feature.find('img', class_='property24generic_icon_garages_25').find_next_sibling('span').string.strip())

                extra_details = soup.find_all('div', class_='sc_listingSummaryRow')

                if extra_details and len(extra_details) > 0:
                    for detail in extra_details:
                        if detail.find('div', class_='detailItemName').find(string='Type of Property'):
                            new_prop.category = detail.find('div', class_='detailItemName').find_next_sibling('div',class_='detailItemValues').find(
                                'div').string.strip()

                        if detail.find('div', class_='detailItemName').find(string='List Date'):
                            new_prop.list_date = detail.find('div', class_='detailItemName').find_next_sibling('div', class_='detailItemValues').find(
                                'div').string.strip()

                        pattern = re.compile(r'\s*%s\s*' % 'Erf Size')
                        patter2 = re.compile(r'\s*%s\s*' % 'Floor Area')

                        value_pattern = re.compile(r'(?s).*')

                        if detail.find('div', class_='detailItemName').find(text=pattern):
                            new_prop.erf_size = detail.find('div', class_='detailItemValues').get_text().strip()

                        if detail.find('div', class_='detailItemName').find(text=patter2):
                            new_prop.floor_area = detail.find('div', class_='detailItemValues').get_text().strip()

                        # map cordinates
                        script = str(soup.find_all('script'))
                        cordinate_pattern = re.compile('google.maps.LatLng\(\'(-?\d{1,3})(\.)(\d+\')(,\')(-?\d{1,3}\.)(\d+\'\))')

                        if script and len(script) > 0:
                            pattern = re.compile('google.maps.LatLng\(\'(-?\d{1,3})(\.)(\d+\')(,\')(-?\d{1,3}\.)(\d+\'\))')
                            result = re.search(pattern, script)

                            latitude_pattern = re.compile('\(\'-?\d{1,3}(\.)(\d+\')')
                            longitude_pattern = re.compile(',\'(-?\d{1,3}\.)(\d+\'\))')

                            if result:
                                string = result.group()
                                lat = re.search(latitude_pattern, string)
                                longitude = re.search(longitude_pattern, string)
                                if lat:
                                    new_prop.latitude = lat.group()
                                if longitude:
                                    new_prop.longitude = longitude.group()

                        print(new_prop.__dict__)
                        self.writer.writerow(new_prop.__dict__)

                        break
            except: # If error, delete this proxy and find another one
                del self.proxies[proxy_index]
                print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
                proxy_index = self.random_proxy()
                proxy = self.proxies[proxy_index]


if __name__ == "__main__":
    scraper = Scraper()

    pages = 315
    query = {'&Page':1}

    counter = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = 'https://www.property24.co.ke/property-for-sale-in-nairobi-c1890?PropertyTypes=houses%2Capartments-flats%2Ctownhouses'

    scraper.retrieveProxies()

    def getPageUrlsAndData(currentPage):
        query['Page'] = currentPage
        global counter

        response = requests.get(url,params=query,headers=headers)
        soup = BeautifulSoup(response.text,'html.parser')
        result = soup.select('div.sc_panelWrapper div div.sc_panel.sc_listingTile')
        p = soup.find_all("a", class_="title")

        for i in p:
            print('----------Link Extracted------------\n')#Property link has been extracted
            time.sleep(1)
            scraper.scrape(scraper.base_url + i.get('href'), scraper.ua.random)
            time.sleep(1)
            print('----------Scraped Data--------------\n')
        for p in range(3,pages+1):
            print('------------Fetching Page ',p ,'-----------')
            getPageUrlsAndData(p)