import csv
import bs4
import requests
from fake_headers import Headers
import time


def get_headers():
    return Headers(os="win", browser="chrome").generate()


response = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2", headers=get_headers())
main_html_data = response.text

main_soup = bs4.BeautifulSoup(main_html_data, features="lxml")

tag_div_list = main_soup.find("main", class_="vacancy-serp-content")

div_tags = tag_div_list.find_all('div', class_='serp-item')

parsed_data = []

for div_tag in div_tags:
    h3_tag = div_tag.find("h3", class_="bloko-header-section-3")
    a_tag = h3_tag.find("a")
    absolute_link = a_tag["href"]
    title = h3_tag.text
    div_tags_company = div_tag.find("div", class_="vacancy-serp-item-company")
    salary = div_tag.find('span', attrs={"data-qa": "vacancy-serp__vacancy-compensation"})
    if salary is not None:
        salary = salary.text
        salary = salary.replace("\u202f", "")
    else:
        salary = "Зарплата не указана"

    time.sleep(0.2)
    div_response = requests.get(absolute_link, headers=get_headers())
    div_html_data = div_response.text
    div_soup = bs4.BeautifulSoup(div_html_data, features="lxml")

    full_div_tag = div_soup.find("div", class_="vacancy-section")
    div_tag_text = full_div_tag.text
    info_vacancy_div = div_soup.find("div", class_="vacancy-company-redesigned")
    company_name = info_vacancy_div.find("div", class_="vacancy-company-details").text
    j = 0
    for i in range(3):
        if company_name[i] == "О":
            j += 1
        if j == 3:
            company_name = company_name.replace("\xa0", " ")
    company_address = info_vacancy_div.find("span", attrs={"data-qa": "vacancy-view-raw-address"})
    if company_address is not None:
        company_address = company_address.text
    else:
        company_address = div_soup.find("p", attrs={"data-qa": "vacancy-view-location"}).text

    if "Django" in div_tag_text or "Flask" in div_tag_text:
        parsed_data.append(
            {
                "Link": absolute_link,
                "Salary": salary,
                "Company Name": company_name,
                "Company Address": company_address
            }
        )

with open("vacancies.csv", "w", encoding="utf-8") as csvfile:
    fieldnames = ["Link", "Salary", "Company Name", "Company Address"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in parsed_data:
        writer.writerow(item)
