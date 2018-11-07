import requests
from bs4 import BeautifulSoup


def scrape():
    """
    Scrape Lotto wins from the https://mylotto.co.ke website
    """
    base_url = "https://mylotto.co.ke"
    print("Initialising soup...")
    small_soup = BeautifulSoup(requests.get(
        "https://mylotto.co.ke/all-results").content, "lxml")
    count = 0
    for row in small_soup.find('table', class_="winner-table").tbody.children:
        if row != "\n":
            count += 1
            cells = row.find_all("td")
            next_link = cells[5].a.get("href")
            print(str(count)+" Getting "+cells[0].string+" ...")
            with open("lotto/"+cells[0].string+".csv", "w") as file:
                inner_soup = BeautifulSoup(requests.get(
                    base_url+next_link).content, "lxml")
                file.write("matched,price,total_winners\n")
                for inner_row in inner_soup.find("table", class_="winner-table").tbody.children:
                    if inner_row != "\n":
                        inner_cells = inner_row.find_all("td")
                        file.write(",".join([
                            inner_cells[0].string.strip(),
                            inner_cells[1].string.strip().replace(",", ""),
                            inner_cells[2].string.strip(
                            )+"\n" if inner_cells[2].string else "\n"
                        ])
                        )


if __name__ == '__main__':
    scrape()
