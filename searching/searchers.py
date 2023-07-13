from . import Searcher, SearchResult
from markdownify import markdownify
from selenium import webdriver
import requests
import re
import bs4

class RTDSearcher(Searcher):
    '''Поиск по документации на портале Read The Docs'''
    def __init__(self, token, project):
        self.token = token
        self.project = project
    def search(self, query):
        response = requests.get(
            "https://readthedocs.org/api/v3/search/",
            headers = { "Authorization": f"Token {self.token}" },
            params = { "q": f"project:{self.project} {query}" }
        )

        json_response = response.json()
        import json
        print(json.dumps(json_response, indent=2))

        return SearchResult([
            (
                result["title"],
                result["domain"] + result["path"],
                "\n".join([
                    markdownify(
                        "\n".join(block["highlights"].get("content")) or\
                        "\n".join(block["highlights"].get("title"))
                    )
                    for block in result["blocks"]
                ])
            )
            for result in json_response["results"]
        ])

class MicroimpulsSearcher(Searcher):
    '''Поиск по документации на сайте Microimpuls'''

    def search(self, query):
        page = requests.get(
            "https://microimpuls.com",
            params={
                "post_type": "docs",
                "s": query
            }
        )

        return SearchResult([
            (
                markdownify(post.select_one("p.news-text").text),
                post.select_one("a").attrs["href"],
                markdownify(post.select_one("p.small-description-product").text)
            )
            for post in bs4.BeautifulSoup(page.text, features="lxml").select('div[id^="post"]')
        ])


class GithubPagesSearcher(Searcher):
    def __init__(self, path):
        self.path = path
        self.page = None

    def cache(self):
        options = webdriver.FirefoxOptions(); options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        driver.get('https://microimpuls.github.io/smarty-billing-api-docs/')
        self.page = bs4.BeautifulSoup(driver.page_source, features="lxml")
        driver.close()

    def search(self, query):
        if self.page == None:
            self.cache()

        result = []

        sections = self.page.select("div#sections section")
        for section in sections:
            head = section.find("h1").text
            articles = section.select("article")

            for article in articles:
                name = article.find("h1").text
                if not re.search(query, name):
                    continue

                method = article.select_one(".method").text
                url = article.select_one(".language-http").text
                print("  ", name)
                print("    ", method, url)

                table_of_params = []

                parameter_heads = article.select("h2")
                for parameter_head in parameter_heads:
                    parameters = parameter_head.find_next_sibling("table")
                    table = str(parameters).replace('\n', '')
                    m = markdownify(table)
                    table_of_params.append(m)

                result.append((name, self.path,  '\n' + url + '\n' + ''.join(table_of_params)))
        print(*result, sep='\n')
        return SearchResult(result)
