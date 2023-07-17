from mmpy_bot import Plugin, Message
from mmpy_bot import listen_to
from searching.searchers import RTDSearcher, MicroimpulsSearcher, GithubPagesSearcher
from searching.searchers import JsDocSearcher, MattermostHistorySearcher
from searching.searchers import YandexWikiSearcher
import json

try:
    with open('config.json', "r") as config_file:
        config = json.loads(config_file.read())
        RTD_TOKEN = config["readthedocs_token"]
        MM_TOKEN = config["mattermost_token"]
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
            MattermostHistorySearcher(
                MM_TOKEN, "https://bottestformicro.cloud.mattermost.com",
                "u3nwyiepx78kbkdtd58it1dp3o")
        ]

        self.wiki = [
            YandexWikiSearcher(YANDEX_LOGIN, YANDEX_PASSW)
        ]

    @listen_to("^alive$")
    async def alive(self, message: Message):
        self.driver.reply_to(message, "I'm alive!")

    @listen_to("^wiki (.*)$")
    async def search(self, message: Message, expr: str):
        self.driver.reply_to(message, "#### Results:")
        for searcher in self.wiki:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, row)

    @listen_to("^rtd (.*)$")
    async def search_in_smarty(self, message: Message, expr: str):
        self.driver.reply_to(message, "#### Results:")
        for searcher in self.readthedocs:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, row)

    @listen_to("^micro (.*)$")
    async def search_in_microimpuls(self, message: Message, expr: str):
        self.driver.reply_to(message, "#### Results:")
        for searcher in self.micro:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, row)

    @listen_to("^gitdev (.*)$")
    async def search_in_gitdocs(self, message: Message, expr: str):
        self.driver.reply_to(message, "#### Results:")
        for searcher in self.devdocs:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, row)

    @listen_to("^history (.*)$")
    async def search_in_mattermost_history(self, message: Message, expr: str):
        self.driver.reply_to(message, f"#### Results:")
        for searcher in self.history:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, row)
