import discord
import asyncio
from datetime import datetime, timedelta

client = discord.Client()

@client.event
async def on_ready():
    print('Snapchat bot ready!')

@client.event
async def on_message(message):
    if message.content.startswith('!snapchat_bot_status'):
        await client.send_message(message.channel, 'I am awake!')
    if message.content.startswith('!snapchat_bot_help'):
        await client.send_message(message.channel, 'Use !snapchat_bot_status to check if the bot is awake, and !snapchat_bot_purge to delete all messages in the #snapchat channel')
    if message.content.startswith('!snapchat_bot_purge'):
        channel = discord.utils.find(lambda c: c.name == 'snapchat', client.get_all_channels())
        await client.purge_from(channel)

async def snapchat_bot():
    await client.wait_until_ready()
    print("Purging")
    channel = discord.utils.find(lambda c: c.name == 'snapchat', client.get_all_channels())
    while not client.is_closed:
        future = datetime.utcnow() - timedelta(hours=24)
        #future = datetime.utcnow() - timedelta(minutes=5)
        await client.purge_from(channel, before=future)
        await asyncio.sleep(60)



client.loop.create_task(snapchat_bot())
client.run('key')
