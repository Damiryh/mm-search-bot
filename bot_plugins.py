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
    def __init__(self):
        super().__init__()
        self.searchers = [
            RTDSearcher(RTD_TOKEN, 'mi-smarty-docs'),
            MicroimpulsSearcher(),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-tvmw-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-billing-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-viewstats-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-device-monitoring-api-docs/"),
            GithubPagesSearcher("https://microimpuls.github.io/smarty-content-api-docs/")
        ]

    @listen_to("^wiki (.*)$")
    async def search(self, message: Message, expr: str):
        pass

    @listen_to("^rtd smarty (.*)$")
    async def search_in_smarty(self, message: Message, expr: str):
        result = self.searchers[0].search(expr)
        self.driver.reply_to(message, f"#### Results:\n{ result }")

    @listen_to("^micro (.*)$")
    async def search_in_microimpuls(self, message: Message, expr: str):
        result = searchers[1].search(expr)
        self.driver.reply_to(message, f"#### Results:\n{ result }")

    @listen_to("^gitdev (.*)$")
    async def search_in_github_pages(self, message: Message, expr: str):
        self.driver.reply_to(message, "#### Results:")
        for searcher in self.searchers[2:]:
            result = searcher.search(expr)
            for row in result.rows():
                self.driver.reply_to(message, f"{row}")
