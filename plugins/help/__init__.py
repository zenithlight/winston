import argparse

import argument_parser

#@command
class Help:
    def __init__(self, client):
        self.name = 'help'
        self.client = client
        self.argument_parser = argument_parser.ArgumentParser(description='Get help for commands.', prog='help', add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.initialize_command()

    async def handle_event(self, event):
        if event['type'] == 'command' and event['command'] == 'help':
            try:
                result = self.argument_parser.parse_args(event['arguments'])
            except (ValueError, argparse.ArgumentTypeError) as error:
                await self.client.send_message(event['message'].channel, str(error))
                return

            command = getattr(result, 'command')

            help_string = ''

            if not command:
                for plugin in self.client.plugins:
                    if hasattr(plugin, 'name'):
                        help_string += plugin.argument_parser.format_usage()
            else:
                for plugin in self.client.plugins:
                    if hasattr(plugin, 'name') and plugin.name == command:
                        help_string = plugin.argument_parser.format_help()

            await self.client.send_message(event['message'].channel, help_string)

    def initialize_command(self):
        self.argument_parser.add_argument(
            'command',
            action='store',
            nargs='?',
            type=str,
            help='The command to get help for.'
        )
