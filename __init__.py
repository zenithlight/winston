import discord
import asyncio
import pydrive.auth
import pydrive.drive
import shlex
import os

import settings
from plugins.command import Command
from plugins.roll import Roll
from plugins.help import Help
from plugins.logging import Logging

client = discord.Client()

client.settings = settings.Settings(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))
client.event_queue = asyncio.Queue()

@client.event
async def on_ready():
    client.plugins = [Command(client), Roll(client), Help(client), Logging(client)]
    print('Connected!')

@client.event
async def on_message(message):
    await client.event_queue.put({ 'type': 'message', 'message': message })

@client.event
async def on_message_edit(before, after):
    await client.event_queue.put({ 'type': 'message', 'message': after})

async def process_events():
    await client.wait_until_ready()

    while not client.is_closed:
        event = await client.event_queue.get()

        for plugin in client.plugins:
            await plugin.handle_event(event)

client.loop.create_task(process_events())
client.run(client.settings.data['token'])
