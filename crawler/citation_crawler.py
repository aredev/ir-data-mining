from bs4 import BeautifulSoup
import requests


def get_page_from_author(name):
    """
    Gets the author search page from Google Scholar
    :param name:
    :return:
    """
    r = requests.get("https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors={0}&btnG=".format(name))
    if r.status_code == 200:
        return r.content
    else:
        raise Exception("Author data not retrieved from Google!")


def get_citation_from_author(name):
    """
    Returns the number of citations given an authors name
    """
    name = name.replace(" ", "+")
    page = get_page_from_author(name)

    soup = BeautifulSoup(page, 'html.parser')
    result = soup.find("div", { "class": "gsc_oai_cby" })

    if result:
        result_cited_by_text = result.text
        result_text_splitted = result_cited_by_text.split()

        if len(result_text_splitted) == 3:
            return result_text_splitted[2]
        else:
            raise Exception("Splitted array does not contain three elements.")
    else:
        raise Exception("No such div found.")
