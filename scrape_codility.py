import requests
from bs4 import BeautifulSoup


class Codility:
    def __init__(self, start=1):
        self.start = start
        self.url = "https://app.codility.com"
        print("Connecting to Codility ...")
        self.soup = BeautifulSoup(requests.get(
            self.url+'/programmers/lessons/').content, 'lxml')
        print("Getting Lessons ...")
        self.lessons = [
            self.url+lesson.get("href") for lesson in self.soup.find_all('a', class_="lesson-item")
        ]
        print("{0} Lessons found".format(len(self.lessons)))

    def scrape_lessons(self):
        lesson_count = int(self.start)
        for link in self.lessons[self.start-1:]:
            lesson_soup = BeautifulSoup(requests.get(link).content, 'lxml')
            task_links = [
                t_link.get("href") for t_link in lesson_soup.find_all('a', 'view-button')
            ]
            task_count = 1
            for lnk in task_links:
                print("Scraping Lesson {0} Task {1} ...".format(
                    lesson_count, task_count))
                self.write_task("lesson{0}_{1}".format(lesson_count,
                                                       lnk.split('/')[-2]), self.scrape_task(self.url+lnk))
                task_count += 1
            lesson_count += 1

    def scrape_task(self, url):
        task_soup = BeautifulSoup(requests.get(url).content, 'lxml')
        if task_soup.find('div', class_="desc-py-en") is not None:
            return task_soup.find('div', class_="desc-py-en").text.strip()
        return ""

    def write_task(self, filename, text_content):
        with open(filename, 'w') as task_file:
            task_file.write(text_content)


if __name__ == '__main__':
    new = Codility()
    new.scrape_lessons()
