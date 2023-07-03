from mmpy_bot import Bot, Settings
from bot_plugins import GreetPlugin, SearchPlugin
import json

try:
    with open('config.json', 'r', encoding='utf-8') as config:
        settings = json.loads(config.read())
except IOError as e:
    print(f'Unable to read config: {e}')
    exit(1)

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=settings['mattermost_host'],
        MATTERMOST_PORT=settings['mattermost_port'],
        BOT_TOKEN=settings['mattermost_token'],
        BOT_TEAM=settings['team_name'],
        DEBUG=settings['debug'],
        MATTERMOST_API_PATH='/api/v4',
    ),
	plugins=[GreetPlugin(), SearchPlugin()]
)

if __name__ == '__main__':
    bot.run()
