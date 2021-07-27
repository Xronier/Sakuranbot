import asyncio
import discord
from discord.ext import commands
import time
import sqlite3
from quizquestions import KanjiQuestion
import random


class KanjiQuiz(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='kanjiquiz', help='Start a kanji quiz')
    async def kanji_quiz(self, ctx):
        # await countdown(ctx, 10) # TODO: Remove whenever.

        # Query quiz settings from DB.
        strike_limit = query_settings("SELECT strike_limit FROM quiz_settings")
        level = query_settings("SELECT level FROM quiz_Settings")
        time_limit = query_settings("SELECT time_limit FROM quiz_settings")
        time_flag = query_settings("SELECT time_elapsed_flag FROM quiz_settings")
        acc_flag = query_settings("SELECT acc_flag FROM quiz_settings")
        kanji_flag = query_settings("SELECT end_kanji_flag FROM quiz_settings")

        question_num = 1
        current_strikes = 0
        start = 0
        kanji_list = []

        # If time_flag is true, time the quiz.
        if time_flag:
            start = time.time()

        # Continuously generate questions until strike limit is surpassed.
        while current_strikes < strike_limit:
            kq = KanjiQuestion.generate_question(level)

            # If kanji_flag is true, save each Kanji that shows up.
            if kanji_flag:
                kanji_list.append(kq.get_correct_misc()[0])

            # Generate 4 random positions for the Onyomi to be in.
            answer_positions = random.sample(range(0, 4), 4)

            # Display Question.
            embed = await format_question(question_num, kq, answer_positions, level)
            embed = await ctx.send(embed=embed)
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            await add_reaction(emojis, embed)

            # Wait for user reaction.
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=time_limit,
                                                            check=lambda r, u: u != embed.author and str(
                                                                r.emoji) in emojis)
            except asyncio.TimeoutError:  # User ran out of time.
                await ctx.send("Ran out of time.")
                current_strikes += 1
                await ctx.send("**Current Strikes**: {} of {}".format(current_strikes, strike_limit))
            else:  # User reacted on time, so verify their answer.
                result = await verify_answer(kq, reaction, answer_positions)
                await show_result(ctx, kq, result)
                if not result:
                    current_strikes += 1
                    await ctx.send("**Current Strikes**: {} of {}".format(current_strikes, strike_limit))

            # If the user hasn't hit the strike limit, move onto the next question.
            if current_strikes < strike_limit:
                question_num += 1

        end_msg = "__**Quiz Finished**__"
        # Print misc info (if applicable) after quiz finished.
        if time_flag:
            end_msg += "\n**Time Elapsed**: {:.2f} seconds".format(time.time() - start)
        # If acc_flag true, calculate the user's accuracy during the quiz.
        if acc_flag:
            end_msg += "\n**Accuracy**: {:.2f}%".format(((question_num - current_strikes) / question_num) * 100)
        if kanji_flag:
            end_msg += "\n**Kanji Seen**: {}".format(kanji_list)
        await ctx.send(end_msg)


# Verifies a user's answer based on their reaction.
async def verify_answer(kq, reaction, answer_positions):
    if reaction.emoji == "1️⃣":
        return kq.get_options()[answer_positions[0]] == kq.get_correct()
    elif reaction.emoji == "2️⃣":
        return kq.get_options()[answer_positions[1]] == kq.get_correct()
    elif reaction.emoji == "3️⃣":
        return kq.get_options()[answer_positions[2]] == kq.get_correct()
    elif reaction.emoji == "4️⃣":
        return kq.get_options()[answer_positions[3]] == kq.get_correct()


# Show whether the user got the question correct or not.
async def show_result(ctx, kq, result):
    kanji = kq.get_correct_misc()[0]
    if result:
        embed = discord.Embed(title="Correct! Jisho Link to {}".format(kanji),
                              url="https://jisho.org/search/%23kanji%20{}".format(kanji), color=discord.Colour.green())
        embed = embed.add_field(name="Correct Answer", value="{}".format(kq.get_correct()), inline=False)
        embed = embed.add_field(name="Information", value="{}".format(kq.get_correct_misc_str()))
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Incorrect... Jisho Link to {}".format(kanji),
                              url="https://jisho.org/search/%23kanji%20{}".format(kanji), color=discord.Colour.red())
        embed = embed.add_field(name="Correct Answer", value="{}".format(kq.get_correct()), inline=False)
        embed = embed.add_field(name="Information", value="{}".format(kq.get_correct_misc_str()))
        await ctx.send(embed=embed)


# Query settings DB.
def query_settings(sql):
    db = sqlite3.connect('quiz_settings.sqlite')
    cursor = db.cursor()
    result = cursor.execute(sql).fetchone()[0]
    cursor.close()
    db.close()
    return result


# TODO: Move into KanjiQuestion?
# Format the question received
async def format_question(question_num, kq, answer_positions, level):
    embed = discord.Embed(title="Question: {}".format(question_num))
    embed = embed.add_field(name="What is the reading of {}".format(kq.get_correct_misc()[0]),
                            value=":one: {}\n"
                                  ":two: {}\n"
                                  ":three: {}\n"
                                  ":four: {}".format(kq.get_options()[answer_positions[0]],
                                                     kq.get_options()[answer_positions[1]],
                                                     kq.get_options()[answer_positions[2]],
                                                     kq.get_options()[answer_positions[3]]), inline=False)
    embed = embed.set_footer(text="N{} Kanji Quiz".format(level))
    return embed


# Add reactions to a message given a list of emojis.
async def add_reaction(emojis, embed):
    for e in emojis:
        await embed.add_reaction(emoji=e)


# Countdown
async def countdown(ctx, sec):
    msg = await ctx.send("Starting in {} seconds...".format(sec), delete_after=15)
    while sec != 0:
        sec = sec - 2
        await asyncio.sleep(2)
        await msg.edit(content="Starting quiz in {} seconds...".format(sec))


def setup(client):
    client.add_cog(KanjiQuiz(client))
