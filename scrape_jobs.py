import requests
import csv
from bs4 import BeautifulSoup

baseurl = "https://www.brightermonday.co.ke/jobs?page="
small_soup = BeautifulSoup(requests.get(
    "https://www.brightermonday.co.ke/jobs").content, "lxml")
last_page = int(small_soup.find(
    "ul", class_="pagination").contents[-2].a.string)
paginations = [i for i in range(1, last_page + 1)]
jobs_count = 0

# Open file for writing output
with open("jobs.csv", "w") as job_file:
    fieldnames = [
        "title",
        "location",
        "job_type",
        "employer",
        "category"]
    writer = csv.DictWriter(job_file, fieldnames=fieldnames)
    writer.writeheader()

    # Get the spider
    print("Scraping... ")
    for key, item in enumerate(paginations):
        print("Page " + str(key + 1))
        soup = BeautifulSoup(requests.get(baseurl + str(item)).content, "lxml")
        for job in soup.find_all("article", class_="search-result")[:-1]:

            # Parsing the html
            job_data = {}
            job_data["title"] = job.find(
                "header", class_="search-result__header").a.h3.string
            job_data["location"] = job.find(
                "div", class_="search-result__location").a.string
            job_data["job_type"] = job.find(
                "div", class_="search-result__job-type").contents[1].strip()
            job_data["employer"] = job.find(
                "div", class_="search-result__job-meta").a.string.strip()
            job_data["category"] = job.find(
                "div", class_="search-result__job-category").a.string.strip()
            jobs_count += 1

            # write entries to file
            writer.writerow(job_data)
print("Finished! " + str(jobs_count) + " jobs found.")
