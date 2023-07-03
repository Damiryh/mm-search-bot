from . import Searcher, SearchResult
from markdownify import markdownify
import requests
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
