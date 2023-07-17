from . import Searcher, SearchResult
from markdownify import markdownify
from selenium import webdriver
import requests, re, bs4
from operator import itemgetter
from datetime import datetime
from selenium.webdriver.common.by import By
import json as js

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



class YandexWikiSearcher(Searcher):
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.auth()
        self.cache()

    def auth(self):
        res = requests.get('https://passport.yandex.ru/auth')
        cookies = res.cookies
        action = re.search('https://passport.yandex.ru/auth.*?\"', res.text).group()[:-1]
        csrf_token = re.search('csrf_token".*?".*?"', res.text).group().split('"')[-2]
        retpath = re.search('retpath".*?".*?"', res.text).group().split('"')[-2]
        process_uuid = re.search('process_uuid=.*?"', res.text).group()[:-1].split('=')[1]

        print("Авторизация...")
        res = requests.post('https://passport.yandex.ru/registration-validations/auth/multi_step/start',
            cookies=cookies,
            data={
                'csrf_token': csrf_token,
                'process_uuid': process_uuid,
                'login': self.login,
                'retpath': retpath
            },
            headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
        )

        json = res.json()
        # csrf_token = json['csrf_token']
        track_id = json['track_id']

        print("Аутентификация...")
        res = requests.post('https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password',
            cookies=cookies,
            data={
                'csrf_token': csrf_token,
                'track_id': track_id,
                'password': self.password,
                'retpath': retpath,
                'lang': 'ru'
            },
            headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            },
            allow_redirects=False
        )

        self.cookies = res.cookies

        json = res.json()
        if json['status'] == 'ok':
            print('Аутентификация пройдена успешно')

    def get_menu_items(self, slug):
        session = requests.Session()
        session.cookies = self.cookies
        res = session.get('https://wiki.yandex.ru/?skipPromo=1')

        text = res.text
        csrf_token = re.search('secretkey":".*?"', text).group().split('"')[-2]
        org_id = re.search('orgId":".*?"', text).group().split('"')[-2]

        res = session.post('https://wiki.yandex.ru/.gateway/root/wiki/openNavigationTreeNode', headers={
            'content-type': 'application/json',
            'x-csrf-token': csrf_token,
            'x-org-id': str(org_id)
        }, data=js.dumps({"parentSlug": slug}))

        return res.json()

    def cache(self):
        print('Caching yandex wiki menu tree...')
        self.menu_tree = []

        def visit_node(slug):
            items = [
                (item['slug'], item['title'])
                for item in self.get_menu_items(slug)['children']['results']
            ]

            for slug, title in items:
                visit_node(slug)
                self.menu_tree.append((title, 'https://wiki.yandex.ru/' + slug, ""))

        visit_node("")
        print('Done!')

    def search(self, query):
        result = []

        for item in self.menu_tree:
            if re.search(query, item[0]):
                result.append(item)

        return SearchResult(result)
