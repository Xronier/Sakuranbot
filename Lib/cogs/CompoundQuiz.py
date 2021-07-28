import asyncio
from discord.ext import commands
import time
import sqlite3
from quizquestions import CompoundQuestion


class CompoundQuiz(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='compoundquiz', aliases=['cq'], help='Start a compound quiz')
    async def compound_quiz(self, ctx):
        # await countdown(ctx, 10) # TODO: Remove whenever.

        # Query quiz settings from DB.
        strike_limit = query_settings("SELECT strike_limit FROM quiz_settings")
        c_range = query_settings("SELECT compound_range FROM quiz_Settings")
        time_limit = query_settings("SELECT time_limit FROM quiz_settings")
        time_flag = query_settings("SELECT time_elapsed_flag FROM quiz_settings")
        acc_flag = query_settings("SELECT acc_flag FROM quiz_settings")
        kanji_flag = query_settings("SELECT end_kanji_flag FROM quiz_settings")

        question_num = 1
        current_strikes = 0
        start_time = 0
        kanji_list = []

        # If time_flag is true, time the quiz.
        if time_flag:
            start_time = time.time()

        # Continuously generate questions until strike limit is surpassed.
        while current_strikes < strike_limit:
            # cq = CompoundQuestion.generate_question(c_range, question_num)
            cq = CompoundQuestion.generate_question(c_range, question_num)

            # If kanji_flag is true, save each compound that shows up.
            if kanji_flag:
                kanji_list.append(cq.get_correct_misc()[1])

            embed = await cq.format_question(c_range)
            embed = await ctx.send(embed=embed)
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            await cq.add_reaction(emojis, embed)

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=time_limit,
                                                            check=lambda r, u: u != embed.author and str(
                                                                r.emoji) in emojis)
            except asyncio.TimeoutError:  # User ran out of time.
                await ctx.send("Ran out of time.")
                current_strikes += 1
                await ctx.send("**Current Strikes**: {} of {}".format(current_strikes, strike_limit))
            else:  # User reacted on time, so verify their answer.
                result = await cq.verify_answer(reaction)
                await cq.show_result(ctx, result)
                if not result:
                    current_strikes += 1
                    await ctx.send("**Current Strikes**: {} of {}".format(current_strikes, strike_limit))

            if current_strikes < strike_limit:
                question_num += 1

        end_msg = "__**Quiz Finished**__"
        # Print misc info (if applicable) after quiz finished.
        if time_flag:
            end_msg += "\n**Time Elapsed**: {:.2f} seconds".format(time.time() - start_time)
        # If acc_flag true, calculate the user's accuracy during the quiz.
        if acc_flag:
            end_msg += "\n**Accuracy**: {:.2f}%".format(((question_num - current_strikes) / question_num) * 100)
        if kanji_flag:
            end_msg += "\n**Compounds Seen**: {}".format(kanji_list)
        await ctx.send(end_msg)


def query_settings(sql):
    db = sqlite3.connect('quiz_settings.sqlite')
    cursor = db.cursor()
    result = cursor.execute(sql).fetchone()[0]
    cursor.close()
    db.close()
    return result


# Countdown
async def countdown(ctx, sec):
    msg = await ctx.send("Starting in {} seconds...".format(sec), delete_after=15)
    while sec != 0:
        sec = sec - 2
        await asyncio.sleep(2)
        await msg.edit(content="Starting quiz in {} seconds...".format(sec))


def setup(client):
    client.add_cog(CompoundQuiz(client))
