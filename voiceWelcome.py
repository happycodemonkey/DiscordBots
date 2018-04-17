import discord
import asyncio

client = discord.Client()

@client.event
async def on_ready():
    print('Voice Mod is ready!')

@client.event
async def on_voice_state_update(before, after):
    if after.voice_channel:
        await client.send_message(after,'Thanks for joining the voice channel! Please remember the rules')

client.run('key')
