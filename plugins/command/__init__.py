import os
import shlex
import argparse

import settings
import argument_parser

#@command('command', 'Create command events for messages matching a given prefix.')
class Command:
    def __init__(self, client):
        self.name = 'command'
        self.client = client
        self.settings = settings.Settings(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))
        self.argument_parser = argument_parser.ArgumentParser(description='Create command events for messages matching a given prefix.', prog=self.name, add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.initialize_command()

    async def handle_event(self, event):
        if event['type'] == 'command' and event['command'] == self.name:
            try:
                result = self.argument_parser.parse_args(event['arguments'])
            except (ValueError, argparse.ArgumentTypeError) as error:
                await self.client.send_message(event['message'].channel, str(error))
                return

            if hasattr(result, 'set'):
                self.settings.data['prefix'] = getattr(result, 'value')
                self.settings.save()
                await self.client.send_message(event['message'].channel, 'Set command prefix to: {}'.format(getattr(result, 'value')))

        if event['type'] == 'message':
            message = event['message']
            if message.content.startswith(self.settings.data['prefix']):
                split_text = shlex.split(message.content[len(self.settings.data['prefix']):])
                await self.client.event_queue.put({
                    'type': 'command',
                    'message': message,
                    'command': split_text[0],
                    'arguments': split_text[1:]
                })

    def initialize_command(self):
        subparsers = self.argument_parser.add_subparsers()

        set_parser = subparsers.add_parser('set', help='Set a preference value.')
        set_parser.add_argument('set', type=str, help='The preference key to change.', choices=['prefix'], metavar='key')
        set_parser.add_argument('value', type=str, help='The value to set the key to.')
