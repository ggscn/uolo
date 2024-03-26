import resolve_imports
import discord
from discord import app_commands
import matplotlib.pyplot as plt
from dwh.lib.seasonality import get_seasonality_chart, ranked_seasonality


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=discordchannel))
    print(f'We have logged in as {client.user}')

@tree.command(name = "seasonality", description = "Get stock weekly seasonality",guild=discord.Object(id=discordchannel)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction: discord.Interaction):
    
    print(await interaction.message)
    
    await interaction.response.send_message("Hello!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$szweekly'):
        if '-add' not in message.content:
            plt.close()
        symbol = message.content.split(' ')[1]
        seasonality, file = get_seasonality_chart('weekly', symbol=symbol)
        await message.channel.send(seasonality, file=file)
    
    if message.content.startswith('$sz-kw-weekly'):
        if '-add' not in message.content:
            plt.close()
        keyword = message.content.split(' ')[1]
        seasonality, file = get_seasonality_chart('weekly', keyword=keyword)
        await message.channel.send(seasonality, file=file)

    if message.content.startswith('$szmonthly'):
        if '-add' not in message.content:
            plt.close()
        symbol = message.content.split(' ')[1]
        seasonality, file = get_seasonality_chart('monthly', symbol=symbol)
        await message.channel.send(seasonality, file=file)

    if message.content.startswith('$sz-rank'):
        min_volume = message.content.split(' ')[1]
        try:
            interval_value = int(message.content.split(' ')[2])
        except:
            interval_value = None
        seasonality = ranked_seasonality(
            'monthly', min_volume=int(min_volume), interval_value=interval_value)
        
        await message.channel.send(f"```{seasonality}```")

    

client.run('discordkey')