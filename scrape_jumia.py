from bs4 import BeautifulSoup
import requests
import csv


class JumiaProperty:
    def __init__(self):
        self.title = ""
        self.category = ""
        self.description = ""
        self.price = ""
        self.location = ""
        self.latitude = 0
        self.longitude = 0
        self.bedrooms = 0
        self.bathrooms = 0
        self.fully_furnished = False
        self.car_spaces = 0
        self.land_size = 0
        self.living_area = 0
        self.total_floors = 0
        self.indoor_features = []
        self.outdoor_features = []
        self.eco_features = []


class JumiaScraper:
    def __init__(self, base_url, category):
        self.category = category
        self.base_url = base_url
        self.soup = BeautifulSoup(requests.get(self.base_url).content, "lxml")
        self.last_page = int(self.soup.find(
            "ul", class_="Pagination").find_all("li")[-2].a.string)
        self.filename = "jumia_"+category.lower().replace(" ", "_")
        self.target_file = open(self.filename, "w")

        fieldnames = ["title", "category", "description", "price", "location", "latitude", "longitude", "bedrooms", "bathrooms",
                      "fully_furnished", "car_spaces", "land_size", "living_area", "total_floors", "indoor_features", "outdoor_features", "eco_features"]

        self.writer = csv.DictWriter(self.target_file, fieldnames=fieldnames)
        self.writer.writeheader()

    def scrape(self, url):
        new_prop = JumiaProperty()
        page_soup = BeautifulSoup(requests.get(
            self.base_url+url).content, "lxml")
        for prop_link in page_soup.find_all("div", class_="listing-info"):
            small_soup = BeautifulSoup(
                requests.get("https://house.jumia.co.ke"+prop_link.h3.a.get("href")).content, "lxml")
            new_prop.category = self.category
            new_prop.title = small_soup.find(
                "h1", class_="detail-property-title").string.strip()
            if small_soup.find("td", string="Bedrooms"):
                new_prop.bedrooms = int(small_soup.find(
                    "td", string="Bedrooms").find_next_sibling("td").string.strip())
            if small_soup.find("td", string="Baths"):
                new_prop.bathrooms = int(small_soup.find(
                    "td", string="Baths").find_next_sibling("td").string.strip())
            if small_soup.find("td", string="Car Spaces"):
                new_prop.car_spaces = int(small_soup.find(
                    "td", string="Car Spaces").find_next_sibling("td").string.strip())
            features = small_soup.find_all("div", class_="feature-attribute")
            if features and len(features) > 0:
                for feature in features:
                    if feature.find("h3", string="Eco features:"):
                        new_prop.eco_features = [item.contents[-1].strip() for item in feature.find(
                            "h3", string="Eco features:").find_next_sibling("ul").find_all("li")]
                    elif feature.find("h3", string="Indoor features:"):
                        new_prop.indoor_features = [item.contents[-1].strip() for item in feature.find(
                            "h3", string="Indoor features:").find_next_sibling("ul").find_all("li")]
                    elif feature.find("h3", string="Outdoor features:"):
                        new_prop.outdoor_features = [item.contents[-1].strip() for item in feature.find(
                            "h3", string="Outdoor features:").find_next_sibling("ul").find_all("li")]
                    else:
                        pass
            if small_soup.find("td", string="Fully furnished"):
                new_prop.fully_furnished = small_soup.find(
                    "td", string="Fully furnished").find_next_sibling("td").string.strip()
            if small_soup.find("td", string="Land Size (m²)"):
                new_prop.land_size = float(small_soup.find(
                    "td", string="Land Size (m²)").find_next_sibling("td").string.strip())
            if small_soup.find("td", string="Living area (m²)"):
                new_prop.living_area = float(small_soup.find(
                    "td", string="Living area (m²)").find_next_sibling("td").string.strip())
            if small_soup.find("td", string="Total Floors"):
                new_prop.total_floors = int(small_soup.find(
                    "td", string="Total Floors").find_next_sibling("td").string.strip())
            new_prop.price = small_soup.find(
                "p", class_="property-price").contents[0].strip()[2:]
            new_prop.location = small_soup.find(
                "span", class_="icon-location").string.strip()
            new_prop.latitude = float(small_soup.find(
                "div", class_="map").get("data-lat"))
            new_prop.longitude = float(small_soup.find(
                "div", class_="map").get("data-lng"))
            print(new_prop.__dict__)
            self.writer.writerow(new_prop.__dict__)


def deploy(categories):
    for category in categories:
        jumia = JumiaScraper(category[0], category[1])
        for page in range(1, jumia.last_page+1):
            print("Scraping Page {0}\n".format(page))
            jumia.scrape("?page={0}&size=30".format(page))


if __name__ == "__main__":
    deploy([["https://house.jumia.co.ke/for-sale/", "For Sale"],
            ["https://house.jumia.co.ke/for-rent/", "For Rent"]])
