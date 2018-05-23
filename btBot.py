import discord
import asyncio
import json

from testbot import TestBot
from pollbot import PollBot

class BtBotClient(discord.Client):
    """ discord.py v1.0.0a0 client """
    def __init__(self):
        super().__init__()
        self.testBot = TestBot(self)
        self.pollBot = PollBot(self)

    async def on_ready(self):
        print('BT bot ready!')

    async def on_message(self, message):
        await self.testBot.handleMessage(message)
        await self.pollBot.handleMessage(message)

if __name__ == "__main__":
    configData = None
    with open('clientconfig_privatetesting.json') as configFile:
        configData = json.load(configFile)

    client = BtBotClient()
    client.run(configData['token'])
