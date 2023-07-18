from mmpy_bot import Plugin, Message
from mmpy_bot import listen_to
from searching.searchers import RTDSearcher, MicroimpulsSearcher, GithubPagesSearcher
from searching.searchers import JsDocSearcher, MattermostHistorySearcher
from searching.searchers import YandexWikiSearcher
from searching import SearchResult
import threading, schedule, time
import json

try:
    with open('config.json', "r") as config_file:
        config = json.loads(config_file.read())
        RTD_TOKEN = config["readthedocs_token"]
        MM_TOKEN = config["mattermost_token"]
        MM_URL = config["mattermost_url"]
        MM_TEAM_ID = config["mattermost_team_id"]
        YANDEX_LOGIN = config["yandex_login"]
        YANDEX_PASSW = config["yandex_password"]
        
except IOError as e:
    print(f'Unable to read config: {e}')
    exit(1)
except KeyError as e:
    print(f'Cannot find value in cconfig: {e}')
    exit(1)

class GreetPlugin(Plugin):
    @listen_to("greet")
    async def greet(self, message: Message):
        self.driver.reply_to(message, "# Hello, World!")

class SearchPlugin(Plugin):
    def __init__(self):
        super().__init__()

        self.stopped = threading.Event()
        
        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not self.stopped.is_set():
                    schedule.run_pending()
                    time.sleep(1)

        schedule_thread = ScheduleThread()
        schedule_thread.start()
        
        self.devdocs = [
            GithubPagesSearcher("https://microimpuls.github.io/smarty-tvmw-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-billing-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-viewstats-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-device-monitoring-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-content-api-docs/"),
            JsDocSearcher("https://microimpuls.github.io/justify-impuls-screens-jsdoc/"),
            JsDocSearcher("https://microimpuls.github.io/justify-engine-main-jsdoc/"),
            JsDocSearcher("https://microimpuls.github.io/justify-impuls-main-jsdoc/")
        ]

        self.readthedocs = [
            RTDSearcher(RTD_TOKEN, 'mi-smarty-docs')
        ]

        self.micro = [
            MicroimpulsSearcher()
        ]

        self.history = [
            MattermostHistorySearcher(MM_TOKEN, MM_URL, MM_TEAM_ID)
        ]
        
        self.wiki = [
            YandexWikiSearcher(YANDEX_LOGIN, YANDEX_PASSW)
        ]

        self.gs = self.devdocs + self.readthedocs + self.wiki + self.micro

    def __del__(self):
        self.stopped.set()

    def search(self, searchers, message, expr):
        self.driver.reply_to(message, "#### Results:")
        for searcher in searchers:
            result = searcher.search(message, expr)
            for row in result.rows():
                self.driver.reply_to(message, row)
        print('===== Завершено! =====')

    @listen_to("^alive$")
    async def alive(self, message: Message):
        self.driver.reply_to(message, "I'm alive!")

    @listen_to("^global (.*)")
    async def global_search(self, message: Message, expr: str):
        self.search(self.gs, message, expr)

    @listen_to("^wiki (.*)$")
    async def search_in_wiki(self, message: Message, expr: str):
        self.search(self.wiki, message, expr)

    @listen_to("^rtd (.*)$")
    async def search_in_smarty(self, message: Message, expr: str):
        self.search(self.readthedocs, message, expr)

    @listen_to("^micro (.*)$")
    async def search_in_microimpuls(self, message: Message, expr: str):
        self.search(self.micro, message, expr)

    @listen_to("^gitdev (.*)$")
    async def search_in_gitdocs(self, message: Message, expr: str):
        self.search(self.devdocs, message, expr)

    @listen_to("^history (.*)$")
    async def search_in_mattermost_history(self, message: Message, expr: str):
        self.search(self.history, message, expr)

