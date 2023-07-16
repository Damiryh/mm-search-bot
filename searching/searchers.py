from . import Searcher, SearchResult
from markdownify import markdownify
from selenium import webdriver
import requests, re, bs4
from operator import itemgetter
from datetime import datetime
from selenium.webdriver.common.by import By

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
        driver.get(self.path)
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
                if not re.search(query, name, flags=re.IGNORECASE):
                    continue

                anchor = article.parent['id']
                # print(self.path, anchor)

                method = article.select_one(".method").text
                url = article.select_one(".language-http").text
                # print("  ", name)
                # print("    ", method, url)

                table_of_params = []

                parameter_heads = article.select("h2")
                for parameter_head in parameter_heads:
                    parameters = parameter_head.find_next_sibling("table")
                    table = str(parameters).replace('\n', '')
                    m = markdownify(table)
                    table_of_params.append(m)

                result.append((name, self.path+f"#{anchor}",  '\n' + url + '\n' + ''.join(table_of_params)))
        # print(*result, sep='\n')
        return SearchResult(result)


class JsDocSearcher(Searcher):
    def __init__(self, path):
        self.path = path

    def search(self, query):
        search_result = []
        options = webdriver.FirefoxOptions(); options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        driver.get(self.path)

        input_elem = driver.find_element(By.ID, "search-input")
        button_elem = driver.find_element(By.ID, "search-submit")

        print(input_elem)

        input_elem.send_keys(query)
        button_elem.click()

        search_result_list = driver.find_elements(By.TAG_NAME, "a")
        for elem in search_result_list:
            if elem.text == "" or\
                elem.find_element(By.XPATH, '..').tag_name != "li" or\
                elem.text == "Namespaces" or\
                elem.text == "Classes" or\
                elem.find_element(By.XPATH, '..').find_element(By.XPATH, '..').location.get('y') < 10:
                    continue
            search_result.append((elem.text, elem.get_attribute('href'), ""))

        return SearchResult(search_result)
                

class MattermostHistorySearcher(Searcher):
    def __init__(self, token, url, team_id):
        self.token = token
        self.url = url
        self.team_id = team_id
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}"
        }

    def get_channels_list(self):
        request_channels = requests.get(self.url + '/api/v4/channels', headers=self.headers).json()
        list_of_channels = {}
        for elem in request_channels:
            list_of_channels[elem["id"]] = (elem["name"], elem["display_name"])
        return list_of_channels

    def search(self, query):
        json_params = { 'terms': query, 'is_or_search': True }
        
        response = requests.post(
            self.url + f'/api/v4/teams/{self.team_id}/posts/search',
            headers=self.headers, json=json_params)

        posts = sorted(response.json()['posts'].values(), key=itemgetter('create_at'))
        list_channels = self.get_channels_list()
        search_result = []

        for item in posts:
            unix_timestamp = int(item['create_at'])//1000
            date_string = datetime.fromtimestamp(unix_timestamp).strftime('%d-%m-%Y')
            channel_name = list_channels.get(item['channel_id'], ('', 'Неизвестно'))
            
            search_result.append((
                item['message'],
                self.url + f'/main/channels/{channel_name[0]}#post_{item["id"]}',
                date_string + ": " +
                f"Расположение сообщения: {channel_name[1]}"
            ))

        return SearchResult(search_result)

