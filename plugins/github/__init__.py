import asyncio
import threading
import aiohttp.web

class GitHub:
    def __init__(self, client):
        self.client = client
        self.channel = find_channel(client, 'coders')

        def run_webhook_server():
            server = aiohttp.web.Application(loop=asyncio.new_event_loop())

            async def on_payload(request):
                payload = await request.json()
                event = request.headers['X-GitHub-Event']

                await client.event_queue.put({ 'type': 'github', 'event': event, 'payload': payload })
                return aiohttp.web.Response(status=200)

            server.router.add_route('POST', '/webhooks', on_payload)

            aiohttp.web.run_app(server)

        webhook_server_thread = threading.Thread(target=run_webhook_server)
        webhook_server_thread.daemon = True
        webhook_server_thread.start()

    async def handle_event(self, event):
        if event['type'] == 'github':
            if event['event'] == 'push':
                text = '**{}** pushed {} {} to *{}*:\n'.format(
                    event['payload']['head_commit']['committer']['username'],
                    len(event['payload']['commits']),
                    'commit' if len(event['payload']['commits']) == 1 else 'commits',
                    event['payload']['repository']['name'] + '/' + event['payload']['ref'][11:]
                )

                for commit in event['payload']['commits']:
                    text += '    `{}` {}\n'.format(commit['id'][:8], commit['message'])

            else:
                text = 'GitHub event: ' + event['event']

            await self.client.send_message(self.channel, text)

def find_channel(client, channel_name):
    for server in client.servers:
        for channel in server.channels:
            if channel.name == channel_name:
                return channel
