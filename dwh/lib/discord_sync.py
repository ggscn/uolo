import discord
import requests
from uuid import uuid4

channels = {
    'natgas':'https://discord.com/api/webhooks/discordchannel/discordkey',
    'stocks': 'https://discord.com/api/webhooks/discordchannel/discordkey'
}


class DiscordSyncBot:
    def __init__(self, channel_name='natgas') -> None:
        self.url = channels[channel_name]
        self.session = requests.Session()
        self.webhook = discord.webhook.SyncWebhook.from_url(
            self.url, session=self.session)

    def send(self, text=None, file_binary=None):
        file = None
        if file_binary is not None:
            file = discord.File(fp=file_binary, filename=str(uuid4())+'.png')
        self.webhook.send(text, file=file)

        

