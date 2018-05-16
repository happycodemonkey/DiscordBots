import discord
import asyncio
import json

from testbot import TestBot
from pollbot import PollBot

if __name__ == "__main__":
    configData = None
    with open('clientconfig.json') as configFile:
        configData = json.load(configFile)

    client = discord.Client()
    testbot = TestBot(client)
    pollBot = PollBot(client)

    @client.event
    async def on_ready():
        print('BT bot ready!')

    @client.event
    async def on_message(message):
        await testbot.handleMessage(message)
        await pollBot.handleMessage(message)
            

    client.run(configData['token'])
