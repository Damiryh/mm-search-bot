from mmpy_bot import Plugin, Message
from mmpy_bot import listen_to
from searching.searchers import RTDSearcher, MicroimpulsSearcher, GithubPagesSearcher
import json

try:
    with open('config.json', "r") as config_file:
        RTD_TOKEN = json.loads(config_file.read())["readthedocs_token"]
except IOError as e:
    print(f'Unable to read config: {e}')
    exit(1)

class GreetPlugin(Plugin):
    @listen_to("greet")
    async def greet(self, message: Message):
        self.driver.reply_to(message, "# Hello, World!")

class SearchPlugin(Plugin):
    @listen_to("^(wiki|mi) (.*)$")
    async def search(self, message: Message, source: str, expr: str):
        # TODO Перенести всю логику по отдельным обработчикам
        result = "Empty"
        if source == 'rtd':
            searcher = RTDSearcher(RTD_TOKEN, 'mi-smarty-docs')
        result = searcher.search(expr)
        self.driver.reply_to(message, f"#### Results:\n{ result }")

    @listen_to("^rtd smarty (.*)$")
    async def search_in_smarty(self, message: Message, expr: str):
        result = RTDSearcher(RTD_TOKEN, 'mi-smarty-docs').search(expr)
        self.driver.reply_to(message, f"#### Results:\n{ result }")

    @listen_to("^micro (.*)$")
    async def search_in_microimpuls(self, message: Message, expr: str):
        result = MicroimpulsSearcher().search(expr)
        self.driver.reply_to(message, f"#### Results:\n{ result }")

    @listen_to("^gitdev (.*)$")
    async def search_in_github_pages(self, message: Message, expr: str):
        searchers = [
            GithubPagesSearcher("https://microimpuls.github.io/smarty-tvmw-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-billing-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-viewstats-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-device-monitoring-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-content-api-docs/")
        ]

        for searcher in searchers:
            # result = searcher.search(expr)
            pass

        result = searchers[0].search(expr)
        self.driver.reply_to(message, f"#### Results:\n { result }")
