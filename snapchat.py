import discord
import asyncio
from datetime import datetime, timedelta

client = discord.Client()

@client.event
async def on_ready():
    print('Snapchat bot ready!')


async def snapchat_bot():
    await client.wait_until_ready()
    print("Purging")
    channel = discord.utils.find(lambda c: c.name == 'snapchat', client.get_all_channels())
    while not client.is_closed:
        #future = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        future = future = datetime.utcnow() + timedelta(minutes=1)
        await client.purge_from(channel, before=future)
        await asyncio.sleep(60)

client.loop.create_task(snapchat_bot())
client.run('key')
