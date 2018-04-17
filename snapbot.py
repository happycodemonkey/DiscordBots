import discord
import asyncio
from datetime import datetime, timedelta

class SnapchatBot:
    def __init__(self, client):
        self.client = client
        print('SnapchatBot initialized')
        
    async def snapchat_bot(self):
        await self.client.wait_until_ready()
        print("Purging")
        channel = discord.utils.find(lambda c: c.name == 'snapchat', client.get_all_channels())
        while not self.client.is_closed:
            #future = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            future = future = datetime.utcnow() + timedelta(minutes=1)
            await self.client.purge_from(channel, before=future)
            await asyncio.sleep(60)
