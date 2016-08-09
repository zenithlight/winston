import argparse
import random
import os
import inspect

import settings
import argument_parser

#@command('roll', 'Generate a random number.')
class Roll:
    def __init__(self, client):
        self.name = 'roll'
        self.client = client
        self.settings = settings.Settings(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'))
        self.argument_parser = argument_parser.ArgumentParser(description='Generate a random number.', prog='roll', add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.initialize_command()

    async def handle_event(self, event):
        if event['type'] == 'command' and event['command'] == 'roll':
            try:
                result = self.argument_parser.parse_args(event['arguments'])
            except (ValueError, argparse.ArgumentTypeError) as error:
                await self.client.send_message(event['message'].channel, str(error))
                return

            number = random.randint(getattr(result, 'minimum'), getattr(result, 'maximum'))
            await self.client.send_message(event['message'].channel, 'You rolled a {}.'.format(number))

    def initialize_command(self):
        settings = self.settings

        class ValidateMinimum(argparse.Action):
            def __call__(self, parser, namespace, value, option_string=None):
                if value < settings.data['minimum']:
                    raise argparse.ArgumentTypeError('The minimum roll can\'t be less than {}.'.format(settings.data['minimum']))

                setattr(namespace, self.dest, value)

        self.argument_parser.add_argument(
            'minimum',
            action=ValidateMinimum,
            nargs='?',
            default=self.settings.data['minimum'],
            type=int,
            help='The lowest number that can be generated.'
        )

        class ValidateMaximum(argparse.Action):
            def __call__(self, parser, namespace, value, option_string=None):
                if value < getattr(namespace, 'minimum'):
                    raise argparse.ArgumentTypeError('The maximum roll amount can\'t be more than the minimum.')
                if value > settings.data['maximum']:
                    raise argparse.ArgumentTypeError('The maximum roll can\'t be more than {}.'.format(settings.data['maximum']))

                setattr(namespace, self.dest, value)

        self.argument_parser.add_argument(
            'maximum',
            action=ValidateMaximum,
            nargs='?',
            default=6,
            type=int,
            help='The highest number that can be generated.'
        )
