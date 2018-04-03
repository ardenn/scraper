import requests
import csv
from bs4 import BeautifulSoup

base_url = "http://quotes.toscrape.com"
paginations = [i for i in range(1, 11)]
my_data = {}

print("Scraping...")
for slug in paginations:
    print("Page " + str(slug))
    soup = BeautifulSoup(
        requests.get(
            base_url +
            "/page/" + str(slug) +
            "/").content,
        "lxml")
    print("\tParsing data...")
    for key, item in enumerate(soup.find_all("div", class_="quote")):
        new_data = {}
        author = item.find("small", class_="author").string
        new_data["text"] = item.span.string
        new_data["tags"] = [
            tag.string for tag in item.find_all(
                "a", class_="tag")]
        if author in my_data:
            new_data["birthday"] = my_data[author]["birthday"]
            new_data["description"] = my_data[author]["description"]
        else:
            about_link = item.a.get("href")
            new_soup = BeautifulSoup(
                requests.get(
                    base_url +
                    about_link).content,
                "lxml")
            new_data["birthday"] = new_soup.find(
                "span", class_="author-born-date").string
            new_data["description"] = new_soup.find(
                "div", class_="author-description").string
        my_data[author] = new_data

print("Finished!!, Found " + str(len(my_data)) + " quotes.")
