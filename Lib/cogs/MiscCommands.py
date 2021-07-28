from discord.ext import commands
import asyncpraw
import random
import discord.embeds


class MiscCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="sponge")
    async def sponge(self, ctx):
        reddit = asyncpraw.Reddit(client_id="XlF4b8x_KSv3FVW8du3F7Q",
                                  client_secret="ZzpVbtdbLcfQZOyGPa8n6SjtUTzWrw",
                                  user_agent="Sakuranbot")

        sponge_submissions = await reddit.subreddit('BikiniBottomTwitter')
        sub = random.choice([meme async for meme in sponge_submissions.top(time_filter="month", limit=25)])

        embed = discord.Embed(title="{}".format(sub.title), description="Author: u/{}".format(sub.author.name),
                              color=discord.Color.gold())
        embed = embed.set_image(url=sub.url)
        embed = embed.set_footer(text="👍 {} 💬 {}".format(sub.score, sub.num_comments))
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(MiscCommands(client))
