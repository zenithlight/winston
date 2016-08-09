import os
import croniter
import pydrive.auth
import pydrive.drive
import datetime
import argparse

import settings
import argument_parser

#@command('logging', 'Save messages to Google Drive.')
class Logging:
    def __init__(self, client):
        self.name = 'logging'
        self.client = client
        self.settings = settings.Settings(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))
        self.argument_parser = argument_parser.ArgumentParser(description='Save messages to Google Drive.', prog='logging', add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.initialize_command()

        self.google_auth = pydrive.auth.GoogleAuth()
        self.google_auth.CommandLineAuth()
        self.google_drive = pydrive.drive.GoogleDrive(self.google_auth)

        # self.logging = False
        # self.dirty = False # whether we have to update the file or not
        # self.start_cron = croniter.croniter(self.settings.data['start'])
        # self.stop_cron = croniter.croniter(self.settings.data['stop'])
        #
        # self.client.loop.run_until_complete(self.start_logging_maybe())

    async def start_logging_maybe(self):
        await self.client.wait_until_ready()

        self.channel = self.find_channel(self.settings.data['channel'])

        previous_start = self.start_cron.get_prev()
        previous_stop = self.stop_cron.get_prev()

        if (previous_stop < previous_start):
            await self.start_logging()

    async def handle_event(self, event):
        if event['type'] == 'command' and event['command'] == 'logging':
            try:
                event['message'].content = event['message'].clean_content # fix channels in titles being an id instead of the channel name
                result = self.argument_parser.parse_args(event['arguments'])
            except (ValueError, argparse.ArgumentTypeError) as error:
                await self.client.send_message(event['message'].channel, str(error))
                return

            if getattr(result, 'start'):
                # await self.start_logging()
                return

            if getattr(result, 'stop'):
                # await self.stop_logging()
                return

            if getattr(result, 'force'):
                await self.force_log(getattr(result, 'channel'), getattr(result, 'limit'), getattr(result, 'title'))

        # if event['type'] == 'message':
        #     message = event['message']
        #
        #     if message.channel == self.channel and self.logging:
        #         line = format_message(self.settings.data['format'], message)
        #         self.file.SetContentString(self.file.GetContentString() + line + '\n')
        #         self.dirty = True

    async def start_logging(self):
        await self.client.wait_until_ready()

        self.file = google_drive.CreateFile({'title': self.settings.data['title'].format(channel=self.settings.data['channel'], date=datetime.datetime())})
        self.file.upload()
        self.logging = True

        self.client.call_later(self.settings.data['interval'] / 1000, self.update_soon)
        self.client.loop.call_at(self.stop_cron.get_next(), self.stop_logging_soon)

        await self.client.send_message(self.channel, 'Started logging.')

    def start_logging_soon(self):
        self.client.loop.run_until_complete(start_logging)

    async def stop_logging(self):
        await self.client.wait_until_ready()

        self.logging = False

        self.client.loop.call_at(self.start_cron.get_next(), self.start_logging_soon)
        await self.client.send_message(self.channel, 'Stopped logging.')

    def stop_logging_soon(self):
        self.client.loop.run_until_complete(stop_logging)

    async def update(self):
        await self.client.wait_until_ready()

        if self.dirty:
            self.file.upload()

        self.dirty = False

        self.client.call_later(self.settings.data['interval'] / 1000, self.update_soon)

    def update_soon(self):
        self.client.loop.run_until_complete(update)

    def find_channel(self, channel_name):
        for server in self.client.servers:
            for channel in server.channels:
                if channel.name == channel_name:
                    return channel

    async def force_log(self, channel_name, limit, title): # archives all previous messages in a channel
        channel = self.find_channel(channel_name)
        content = ''
        log_file = self.google_drive.CreateFile({'title': title, 'parents': [{'id': self.settings.data['folder']}]})

        message_list = []
        async for message in self.client.logs_from(channel, limit=limit):
            message_list.append(message)

        content = ''
        for message in message_list[::-1]:
            content += format_message(self.settings.data['format'], message) + '\n'

        log_file.SetContentString(content)
        log_file.Upload()

        await(self.client.send_message(channel, 'Force logging complete.'))

    def initialize_command(self):
        self.argument_parser.add_argument('--start', action='store_true', help='Start logging the pre-configured channel.')
        self.argument_parser.add_argument('--stop', action='store_true', help='Stop logging the pre-configured channel.')
        self.argument_parser.add_argument('--force', action='store_true', help='Force logging the specified channel.')
        self.argument_parser.add_argument('channel', action='store', type=str, nargs='?', help='Name of the channel to force logs for.')
        self.argument_parser.add_argument('limit', action='store', type=int, nargs='?', help='Maximum number of messages to retrieve.')
        self.argument_parser.add_argument('title', action='store', type=str, nargs='?', help='Title of the Google Drive document.')

def format_message(format_string, message):
    return format_string.format(author=message.author.name, date=message.timestamp, message=message.clean_content)
