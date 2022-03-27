from typing import Type
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command
import aiohttp
import base64


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("archivebox_base_url")
        helper.copy("username")
        helper.copy("password")
        print("HI!")
        print(self["archivebox_base_url"])
        print(self["username"])
        print(self["password"])


def client_api_session(config):
    token = base64.b64encode(
        bytes(f"{config['username']}:{config['password']}", "utf-8")
    ).decode("utf-8")
    return aiohttp.ClientSession(
        config["archivebox_base_url"], headers={"Authorization": f"Basic {token}"}
    )


class ArchiveBoxBot(Plugin):
    async def start(self) -> None:
        self.config.load_and_update()

    @command.new(name="archive")
    @command.argument("url", pass_raw=True, required=True)
    async def archive(self, evt: MessageEvent, url: str) -> None:
        async with client_api_session(self.config) as session:
            try:
                async with session.post(
                    "/api-gateway/page", data={"url": url}
                ) as response:
                    if response.status != 200:
                        await evt.reply(
                            f"Sorry, I received an invalid response from ArchiveBox: {response.status}"
                        )
                        return
                    data = await response.json()
                    await evt.reply(
                        f"`{data['title']}`\n\nArchived {data['date']}: {data['url']}"
                    )
            except Exception as e:
                await evt.reply(
                    f"Sorry, there's a problem with ArchiveBox right now: {e}"
                )

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config
