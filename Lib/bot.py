import os
import random

import sqlite3

from discord.ext.commands import bot
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    if not os.path.exists(os.getcwd() + "\\database"):
        os.mkdir(os.getcwd() + "\\database")
    else: # DELETE
        print("database folder exists")

    print(f'{client.user.name} has connected.\n')


# Allows cogs to be loaded during runtime.
@client.command(name='load')
async def load_cog(ctx, extension):
    client.load_extension(f'cogs.{extension}')


# Allows cogs to be unloaded during runtime.
@client.command(name='unload')
async def unload_cog(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


# Allows cogs to be reloaded during runtime.
@client.command(name='reload')
async def reload_cog(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


# Loads all cogs in the cogs folder
for f in os.listdir('./cogs'):
    if f.endswith('.py'):
        client.load_extension(f'cogs.{f[:-3]}')


@client.command(name='Who?', help='Tells you who the bot is')
async def say_name(ctx):
    paul_quotes = ['Me paul.', 'Me Sangres.']
    response = random.choice(paul_quotes)
    await ctx.send(response)

client.run(TOKEN)
