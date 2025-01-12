# This file represents the quiz settings for ALL quizzes.
import os
from discord.ext.commands import bot
from discord.ext import commands
import sqlite3


# Important note: Any updates to the database require the binding variable to be a tuple. Even if you're only adding one
# thing, you must surround the statement with parenthesis and add a comma after the variable.
# Example: val = (",".join(args),)
class QuizSettings(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Database initializes on ready.
    @bot.Cog.listener()
    async def on_ready(self):
        print('Quiz potion loaded')
        # If the database for quiz_settings doesn't exist, create it.
        try:
            os.chdir(os.getcwd() + "\\database")
            if not os.path.exists("quiz_settings.sqlite"):  # May be useless since cursor makes db if it doesn't exist.
                print("Missing quiz_setting database, making")
                db = sqlite3.connect('quiz_settings.sqlite')
                cursor = db.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_settings(
                    level TEXT,
                    time_limit INTEGER,
                    acc_flag INTEGER,
                    end_kanji_flag INTEGER,
                    time_elapsed_flag INTEGER,
                    strike_limit INTEGER,
                    compound_range TEXT
                    )
                ''')
                # Insert generic quiz settings if none exist.
                cursor.execute(
                    f"INSERT INTO quiz_settings(level, time_limit, acc_flag, end_kanji_flag, time_elapsed_flag, strike_limit, compound_range)"
                    f"VALUES (5, 15, 1, 1, 1, 3, '1,500')")
                db.commit()
                cursor.close()
                db.close()
        except FileNotFoundError:
            print("Database folder doesn't exist! Should have initialized on bot boot.")

    # Displays quiz settings
    @commands.command(name='qs', help='Displays quiz settings')
    async def quiz_settings(self, ctx):
        # Options for users to change quiz settings.
        db = sqlite3.connect('quiz_settings.sqlite')
        cursor = db.cursor()
        await ctx.send(":tools: Quiz Settings: :tools:\n"
                       "Change levels: JLPT level(s) **{}** (.setkqlevel)\n"
                       "Change time limit (in sec) per question: **{}** (.settime)\n"
                       "Toggle show accuracy at the end of a quiz: **{}** (.toggleacc)\n"
                       "Toggle show kanji at the end of a quiz: **{}** (.togglekanji)\n"
                       "Toggle show total elapsed time at the end of a quiz: **{}** (.toggletime)\n"
                       "Change the total strike allowed for a quiz: **{}** (.setstrike)\n"
                       "Change range: **{}** (.setcqlevel)"
                       .format(cursor.execute("SELECT level FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT time_limit FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT acc_flag FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT end_kanji_flag FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT time_elapsed_flag FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT strike_limit FROM quiz_settings").fetchone()[0],
                               cursor.execute("SELECT compound_range FROM quiz_settings").fetchone()[0]))

    @commands.command(name='setkqlevel', help='Change which Kanji show up on the kanji quiz')
    async def set_kq_level(self, ctx, *args):
        possible_levels = ["0", "1", "2", "3", "4", "5"]
        if len(args) > 0 and (len(set(args)) == len(args)):
            for i in args:
                if i not in possible_levels:  # Invalid Arguments
                    await ctx.send(
                        "This command allows a user to change the amount of kanji (based on the JLPT) that show"
                        "up on the kanji quiz.\n\n"
                        "**.setkqlevel 5**: Kanji quizzes will only show kanji from JLPT N5\n\n"
                        "**.setkqlevel 4**: Kanji quizzes will only show kanji from JLPT N4\n\n"
                        "**.setkqlevel 3**: Kanji quizzes will only show kanji from JLPT N3\n\n"
                        "**.setkqlevel 2**: Kanji quizzes will only show kanji from JLPT N2\n\n"
                        "**.setkqlevel 1**: Kanji quizzes will only show kanji from JLPT N1\n\n"
                        "**.setkqlevel 0**: Kanji quizzes will only show kanji not on the JLPT\n\n"
                        "A user can also append more arguments to their command to include kanji from more than"
                        "one level.\n"
                        "Example: **.setkqlevel 5 3**: Kanji quizzes will show kanji from ONLY JLPT N5 and N3")
                    break
            # Update database with the given arguments.
            sql = "UPDATE quiz_settings SET level = ?"
            val = (",".join(args),)
            update_setting(sql, val)
            await ctx.send("Level changed.")

        else:  # Arguments don't exist
            await ctx.send(
                "This command allows a user to change the amount of kanji (based on the JLPT) that show"
                "up on the kanji quiz.\n\n"
                "**.setkqlevel 5**: Kanji quizzes will only show kanji from JLPT N5\n\n"
                "**.setkqlevel 4**: Kanji quizzes will only show kanji from JLPT N4\n\n"
                "**.setkqlevel 3**: Kanji quizzes will only show kanji from JLPT N3\n\n"
                "**.setkqlevel 2**: Kanji quizzes will only show kanji from JLPT N2\n\n"
                "**.setkqlevel 1**: Kanji quizzes will only show kanji from JLPT N1\n\n"
                "**.setkqlevel 0**: Kanji quizzes will only show kanji not on the JLPT\n\n"
                "A user can also append more arguments to their command to include kanji from more than"
                "one level.\n"
                "Example: **.setkqlevel 5 3**: Kanji quizzes will show kanji from ONLY JLPT N5 and N3")

    @commands.command(name='setcqlevel', help='Change the range of which words show up on the compound quiz')
    async def set_cq_level(self, ctx, *args):
        db = sqlite3.connect('kanji.sqlite')
        cursor = db.cursor()
        max_freq = cursor.execute("SELECT Frequency FROM compounds LIMIT 1").fetchone()[0]
        if len(args) > 0 and all(x.isnumeric() for x in args):
            if (len(args) == 2 and int(args[0]) <= int(args[1])) or (len(args) == 1 and int(args[0]) <= max_freq):
                # Query
                sql = "UPDATE quiz_settings SET compound_range = ?"
                if len(args) == 2: # Arg is a 2 side range
                    val = (",".join(args),)
                else: # Arg is a one side range.
                    val = (("1," + args[0]),)
                update_setting(sql, val)

            else:
                await ctx.send(
                    "This command allows a user to change the range of which words show up on the compound quiz. "
                    "The lower the range, the higher the frequency. (Min = 1, Max = {})\n\n"
                    "**.setcqlevel 5000**: Compound quizzes will show the most common 5000 words\n\n"
                    "**.setcqlevel 5000 5050**: Compound quizzes will show the 5000th most "
                    "common word to the 5050th (first arg must be less than second).".format(max_freq))
        else:
            await ctx.send("This command allows a user to change the range of which words show up on the compound "
                           "quiz. The lower the range, the higher the frequency. (Min = 1, Max = {})\n\n"
                           "**.setcqlevel 5000**: Compound quizzes will show the most common 5000 words\n\n"
                           "**.setcqlevel 5000 5050**: Compound quizzes will show the 5000th most "
                           "common word to the 5050th (first arg must be less than second).".format(max_freq))

    @commands.command(name='settime', help='Change time limit (in sec) per quiz question')
    async def set_time(self, ctx, arg):
        if 25 >= int(arg) > 2:
            sql = "UPDATE quiz_settings SET time_limit = ?"
            val = (arg,)
            update_setting(sql, val)
            await ctx.send("Time changed.", delete_after=5)
        else:  # Invalid argument
            await ctx.send("This command allows a user to change the amount of time that elapses between each quiz "
                           "question (max time limit = 25 seconds and min = 3 seconds).\n\n"
                           "Example: **.settime 5**: 5 seconds will elapse between each quiz question")

    @commands.command(name='setstrike', help='Set how may strikes are allowed for a quiz.')
    async def set_strike(self, ctx, arg):
        if 5 >= int(arg) > 0:
            sql = "UPDATE quiz_settings SET strike_limit = ?"
            val = (arg,)
            update_setting(sql, val)
            await ctx.send("Strike limit changed.", delete_after=5)
        else:  # Invalid Argument
            await ctx.send("This command allows a user to change the amount of strikes they can accumulate during a "
                           "quiz. When the strike limit is reached, the quiz ends. (max strikes = 5, min = 1)\n\n"
                           "Example: **.setstrike 5**: User is allowed to get 5 questions wrong before the quiz ends.")

    @commands.command(name='toggleacc', help='Toggle show accuracy at the end of a quiz')
    async def toggle_accuracy(self, ctx, arg):
        if int(arg) == 0 or int(arg) == 1:
            sql = "UPDATE quiz_settings SET acc_flag = ?"
            val = arg
            update_setting(sql, val)
            await ctx.send("Accuracy toggled.", delete_after=5)
        else:  # Invalid arguments.
            await ctx.send("This command allows a user to change whether or not to show overall accuracy at the "
                           "end of a quiz.\n\n"
                           "**.toggleacc 1**: Shows accuracy at the end.\n\n"
                           "**.toggleacc 0**: Does not show accuracy at the end.")

    @commands.command(name='togglekanji', help='Toggle show kanji at the end of a quiz')
    async def toggle_kanji(self, ctx, arg):
        if int(arg) == 0 or int(arg) == 1:
            sql = "UPDATE quiz_settings SET end_kanji_flag = ?"
            val = arg
            update_setting(sql, val)
            await ctx.send("Kanji toggled.", delete_after=5)
        else:  # Invalid arguments.
            await ctx.send("This command allows a user to change whether or not to show all kanji that appeared at the "
                           "end of a quiz.\n\n"
                           "**.togglekanji 1**: Shows kanji at the end.\n\n"
                           "**.togglekanji 0**: Does not show kanji at the end.")

    @commands.command(name='toggletime', help='Toggle show total elapsed time at the end of a quiz')
    async def toggle_time(self, ctx, arg):
        if int(arg) == 0 or int(arg) == 1:
            sql = "UPDATE quiz_settings SET time_elapsed_flag = ?"
            val = arg
            update_setting(sql, val)
            await ctx.send("Time toggled.", delete_after=5)
        else:  # Invalid arguments.
            await ctx.send("This command allows a user to change whether or not to show total elapsed time at the "
                           "end of a quiz.\n\n"
                           "**.toggletime 1**: Shows time at the end.\n\n"
                           "**.toggletime 0**: Does not show time at the end.")

    # Catches errors that appear during runtime for the commands above.
    @toggle_kanji.error
    async def toggle_kanji_error(self, ctx, error):
        await ctx.send("This command allows a user to change whether or not to show all kanji that appeared at the "
                       "end of a quiz.\n\n"
                       "**.togglekanji 1**: Shows kanji at the end.\n\n"
                       "**.togglekanji 0**: Does not show kanji at the end.")

    @toggle_time.error
    async def toggle_time_error(self, ctx, error):
        await ctx.send("This command allows a user to change whether or not to show total elapsed time at the "
                       "end of a quiz.\n\n"
                       "**.toggletime 1**: Shows time at the end.\n\n"
                       "**.toggletime 0**: Does not show time at the end.")

    @set_time.error
    async def set_time_error(self, ctx, error):
        await ctx.send("This command allows a user to change the amount of time that elapses between each quiz"
                       "question (max time limit = 25 seconds and min = 3 seconds).\n\n"
                       "Example: **.settime 5**: 5 seconds will elapse between each quiz question")

    @set_strike.error
    async def set_strike_error(self, ctx, error):
        await ctx.send("This command allows a user to change the amount of strikes they can accumulate during a "
                       "quiz. When the strike limit is reached, the quiz ends. (max strikes = 5, min = 1)\n\n"
                       "Example: **.setstrike 5**: User is allowed to get 5 questions wrong before the quiz ends.")

    @toggle_accuracy.error
    async def toggle_accuracy_error(self, ctx, error):
        await ctx.send("This command allows a user to change whether or not to show overall accuracy at the "
                       "end of a quiz.\n\n"
                       "**.toggleacc 1**: Shows accuracy at the end.\n\n"
                       "**.toggleacc 0**: Does not show accuracy at the end.")

    @set_kq_level.error
    async def set_kq_level_error(self, ctx, error):
        await ctx.send("This command allows a user to change the amount of kanji (based on the JLPT) that show"
                       "up on the kanji quiz given quiz.\n\n"
                       "**.setlevel 5**: Kanji quizzes will only show kanji from JLPT N5\n\n"
                       "**.setlevel 4**: Kanji quizzes will only show kanji from JLPT N4\n\n"
                       "**.setlevel 3**: Kanji quizzes will only show kanji from JLPT N3\n\n"
                       "**.setlevel 2**: Kanji quizzes will only show kanji from JLPT N2\n\n"
                       "**.setlevel 1**: Kanji quizzes will only show kanji from JLPT N1\n\n"
                       "A user can also append more arguments to their command to include kanji from more than"
                       "one level.\n"
                       "Example: **setlevel 5 3**: Kanji quizzes will show kanji from ONLY JLPT N5 and N3")


def setup(client):
    client.add_cog(QuizSettings(client))


def update_setting(sql, val):
    db = sqlite3.connect('quiz_settings.sqlite')
    cursor = db.cursor()
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()
