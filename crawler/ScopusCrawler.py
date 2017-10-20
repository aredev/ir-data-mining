from bs4 import BeautifulSoup
import requests
import csv
import time
from urllib.parse import urlparse
from random import randint


def get_content_from_page(url):
    """
    Gets the author search page from Google Scholar
    :param name:
    :return:
    """
    time.sleep(randint(1, 4))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.content
    else:
        raise Exception("Author data not retrieved from Google!")


def get_url_first_page(name):
    """
    Returns the number of citations given an authors name
    """

    first_name = format_first_name(name)
    last_name = format_last_name(name)
    url = 'https://www.scopus.com/results/authorNamesList.uri?origin=searchauthorlookup&src=&st1=' + last_name + '&st2=' + first_name
    page = get_content_from_page(url)

    soup = BeautifulSoup(page, 'html.parser')
    try:
        result = soup.find("a", {"class": "docTitle"}).get('href')
    except:
        result = 'N/A'

    return result


def get_url_second_page(url_string):
    id = url_string.split('authorId=')
    id = id[1].split('&origin')
    id = id[0]

    url = 'https://www.scopus.com/authid/detail.uri?authorId=' + id
    return url


def format_first_name(raw_name):
    name = raw_name.split(' ')
    length = len(name)
    first_name = name[0]

    if length > 2:
        for y in range(1, length - 1):
            first_name = first_name + '+' + name[y]

    return first_name


def format_last_name(raw_name):
    name = raw_name.split(' ')
    length = len(name)
    last_name = name[length - 1]

    return last_name


def find_h_index(page):
    soup = BeautifulSoup(page, 'html.parser')
    result = soup.find("li", {"class": "addInfoRow row3"})
    return result


def crawl(name):
    url1 = get_url_first_page(name)
    if url1 == 'N/A':
        span = url1
    else:

        url2 = get_url_second_page(url1)
        print(url2)
        page = get_content_from_page(url2)
        soup = find_h_index(page)
        spans = soup.find_all("span")

        span = spans[1].text

        try:
            int(span)
        except:
            span = "N/A"

    return span


with open('authors.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    author_list = list(reader)
list = []
a = 0
for x in range(8650, 8660):
    name = author_list[x][1]

    try:
        span = crawl(name)
    except:
        span = 'N/A'
        print('error')
        time.sleep(20)

    list.append([author_list[x][0], name, span])

    print(author_list[x][0], name, span)

    a = a + 1
    if a == 1:
        print('sleep')

        a = 0

        with open('result.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(list)
    time.sleep(randint(4, 7))
