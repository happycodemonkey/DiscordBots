import discord
import asyncio
import json

class TestBot:
    """ Simple test bot"""

    def __init__(self, client):
        self.client = client

    async def handleMessage(self, message):
        if message.content.startswith('!test'):
            counter = 0
            tmp = await message.channel.send('Calculating messages...')
            async for msg in message.channel.history(limit=100):
                if msg.author == message.author:
                    counter += 1

            await tmp.edit(content='You have {} messages.'.format(counter))
        elif message.content.startswith('!sleep'):
            await asyncio.sleep(5)
            await message.channel.send('Done sleeping')
