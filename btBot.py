import discord
import asyncio
from snapbot import SnapchatBot

client = discord.Client()

@client.event
async def on_ready():
    print('BT bot ready!')
    snapbot = SnapChatBot(client)
    testbot = Testbot(client)

client.loop.create_task(snapbot.snapchat_bot())
client.run('key')
