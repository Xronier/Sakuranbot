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
                                  user_agent="Sakuranbot",)

        sponge_submissions = await reddit.subreddit('BikiniBottomTwitter')
        sub = random.choice([meme async for meme in sponge_submissions.top(time_filter="month", limit=50)])
        print(sub.permalink)
        embed = discord.Embed(title="{}".format(sub.title), description="Author: u/{}".format(sub.author.name),
                              color=discord.Color.gold(), url="https://reddit.com{}".format(sub.permalink))
        embed = embed.set_image(url=sub.url)

        sub.comment_sort = 'best'
        sub.comment_limit = 3  # Not sure if more than 1 comment can be stickied, so select first 3
        top_comment = "No comments exists on this post."
        comments = await sub.comments()

        if len(comments) > 0:
            for i in range(3):
                if comments[i].distinguished != "moderator":
                    top_comment = comments[i].body
                    break

        embed = embed.add_field(name="Top Comment", value=top_comment)
        embed = embed.set_footer(text="👍 {} 💬 {}".format(sub.score, sub.num_comments))
        await ctx.send(embed=embed)
        await reddit.close()


def setup(client):
    client.add_cog(MiscCommands(client))
