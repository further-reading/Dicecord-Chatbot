import discord
import time
import asyncio
import datetime
import socket
import traceback
import re
import json

from utils.error_logger import send_error_message
from utils.tokens import saver, token
from utils import textResponses
from utils.roller import Roller
import dbhelpers

SPLATS = ['mage', 'default']


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, o)


def jsonKeys2int(x):
    if isinstance(x, dict):
        return {int(k) if k.isdigit() else k: v for k, v in x.items()}
    return x


class DicecordBot:
    def __init__(self, token, me, dbpath):
        self.token = token
        self.me = me
        self.dbpath = dbpath

    def startBot(self):
        self.loop = asyncio.new_event_loop()
        self.client = discord.Client(loop=self.loop)

        @self.client.event
        async def on_ready():
            """Print details and update server count when bot comes online."""
            content = 'Logged in as'
            content += f'\n{self.client.user.name}'
            content += f'\n{self.client.user.id}'
            content += f'\n{datetime.datetime.now()}'
            send_error_message(content)
            await self.client.change_presence(activity=discord.Game(name='PM "help" for commands'))

        @self.client.event
        async def on_message(message):
            await self.on_message(message)

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == self.client.user:
            return

        try:
            await self.checkCommand(message)
        except TypeError:
            tb = traceback.format_exc()
            self.errorText(message, tb)
            return
        except dbhelpers.db.Error:
            tb = traceback.format_exc()
            self.errorText(message, tb)
            send_error_message(f'SQL error\n{tb}')

    async def send(self, content, message, dm=False):
        if dm:
            member = message.author
            channel = await member.create_dm()
        else:
            channel = message.channel
        try:
            await channel.send(content)
        except (discord.Forbidden, UnicodeEncodeError, discord.errors.HTTPException):
            tb = traceback.format_exc()
            self.errorText(message, tb)

    async def checkCommand(self, message):
        command = message.content.lower()
        if str(message.author) == self.me and "save-cod" in command:
            # allows me to ask for a save of current settings at any time
            await self.send(f'servers:{len(self.client.guilds)}', message)
            await self.client.change_presence(game=discord.Game(name='PM "help" for commands'))
            return

        if message.author.bot:
            return

        if not message.guild:  # Private Message - message.guild = None
            await self.pmCommands(message)
            return

        flavour, splat = dbhelpers.get_flavour(message, self.dbpath)
        character = {'flavour': flavour, 'splat': splat}
        prefix = self.get_prefix(message)
        if prefix == '@mention':
            # we only want bot to respond to @mentions
            pattern = f'<@!?{self.client.user.id}>'
            if not re.search(pattern, command):
                return
        else:
            if not command.startswith(prefix):
                return

        roller = Roller.from_dict(character)
        if 'roll' in command:
            if "chance" in command:
                results = roller.roll_chance(paradox="paradox" in command)
                for result in results:
                    # {0.author.mention} works better for bot implementation
                    out = result.replace('[userID]', "{0.author.mention}")
                    await self.send(out.format(message), message)
                    time.sleep(1)

            else:
                try:
                    results = self.parse_roll(roller, command)
                except RuntimeError:
                    tb = traceback.format_exc()
                    self.errorText(message, f"No dice amount found\n\n{tb}")
                    return
                except:
                    tb = traceback.format_exc()
                    self.errorText(message, f"Unknown error\n\n{tb}")
                    return

                for result in results:
                    out = result.replace('[userID]', "{0.author.mention}")
                    await self.send(out.format(message), message)
                    time.sleep(1)

        elif 'splat' in command:
            out = self.set_splat(message)
            if out:
                out = out.replace('[userID]', "{0.author.mention}")
                out = out.format(message)
                await self.send(out, message)

        elif 'flavour' in command:
            out = self.set_flavour(message)
            if out:
                out = out.replace('[userID]', "{0.author.mention}")
                out = out.format(message)
                await self.send(out, message)

        elif "delete" in command:
            out = self.delete_content(message)
            if out:
                out = out.replace('[userID]', "{0.author.mention}")
                out = out.format(message)
                await self.send(out, message)

        elif "prefix" in command:
            # disabled for now
            return
            # out = self.set_prefix(message)
            # out = out.replace('[userID]', "{0.author.mention}")
            # await self.send(out, message)

    async def pmCommands(self, message):
        command = message.content.lower()

        if 'type' in command:
            content = textResponses.typetext

        elif 'flavourhelp' in command:
            content = textResponses.flavText

        elif 'help' in command:
            content = textResponses.helptext

        elif 'info' in command:
            content = textResponses.aboutText

        else:
            content = "Write 'help' for help, 'info' for bot info or 'type' for list of roll types"

        await self.send(content, message)

    def parse_roll(self, roller, message):
        """Checks text for type of roll, makes that roll."""

        message = message.strip()
        message = message.lower()

        againterm = re.search("(8|9|no)again", message)
        if againterm:
            again = againterm.group(0)
        else:
            again = None

        diceAmount = self.getDiceAmount(message, again)

        if diceAmount is None:
            # stop if no dice number found
            return

        if diceAmount >= 50:
            return ["Too many dice. Please roll less than 50."]

        if again:
            if again =='8again':
                return roller.roll_set(diceAmount, again=8, rote="rote" in message, paradox="paradox" in message)

            elif again =='9again':
                return roller.roll_set(diceAmount, again=9, rote="rote" in message, paradox="paradox" in message)

            elif again =='noagain':
                # no again sets again to 11 so it is impossible to occur
                return roller.roll_set(diceAmount, again=11, rote="rote" in message, paradox="paradox" in message)

        elif "rote" in message:
            return roller.roll_set(diceAmount, rote=True, paradox="paradox" in message)

        elif 'roll' in message:
            return roller.roll_set(diceAmount, paradox="paradox" in message)

    def getDiceAmount(self, messageText, again):
        """

        Args:
            messageText (str): text of message
            again (str or None): whether it is an again term

        Returns (int or None): amount of dice to roll
        """

        if "roll" in messageText:
            # First check for message of the form roll x
            matched = re.search(r'\broll ([0-9]+\b)', messageText)
            if matched:
                return int(matched.group(1))

        if again:
            # Second check for message of the form againTerm x
            matched = re.search(f'(?<=\\b{again} )[0-9]+\\b', messageText)
            if matched:
                return int(matched.group())

        # Check for first number after @mention and then first number in message
        splitMessage = re.split(f'<@{self.client.user.id}>', messageText)
        for message in splitMessage[::-1]:
            matched = re.search(r'\b\d+\b', message)
            if matched is not None:
                return int(matched.group())

    def get_prefix(self, message):
        # not yet implemented
        return '@mention'

    def extract_prefix(self, message):
        # command of form '[current_prefix] prefix {new_prefix}'
        text = message.clean_content.lower()
        command_index = text.index('prefix')
        end_index = command_index + len('prefix')
        prefix = text[end_index:].strip()
        return prefix

    def set_splat(self, message):
        """Allows user to set game type for flavour text."""

        if "check" in message.content.lower():
            _, splat = dbhelpers.get_flavour(message, self.dbpath)
            if splat:
                return f"Splat for [userID] is currently set to {splat} in server {message.guild} - #{message.channel}"
            else:
                return f"Splat for [userID] is currently not set in server {str(message.guild)} - {str(message.channel)}"

        else:
            new_splat = self.find_splat(message.content.lower())
            if new_splat:
                dbhelpers.set_flavour(message, new_splat, self.dbpath)
                return f'Flavour for [userID] changed to {new_splat} in server {message.guild} - #{message.channel}'
            else:
                return 'Unsupported splat selected. Only mage supported at this time.'

    def find_splat(self, message):
        for splat in SPLATS:
            if splat in message:
                return splat

    def set_flavour(self, message):
        """Allows user to set existence of flavour text."""
        setting = message.content.lower()
        if 'off' in setting:
            dbhelpers.set_flavour(message, 'off', self.dbpath)
            return f"Flavour turned off in server {str(message.guild)} - {str(message.channel)}"

        elif 'on' in setting:
            dbhelpers.set_flavour(message, 'on', self.dbpath)
            return f"Flavour turned on in server {str(message.guild)} - {str(message.channel)}"

        elif 'check' in setting:
            flavour, _ = dbhelpers.get_flavour(message, self.dbpath)
            if flavour:
                return f"Flavour turned on in server {str(message.guild)} - {str(message.channel)}"
            else:
                return f"Flavour turned off in server {str(message.guild)} - {str(message.channel)}"

    def delete_content(self, message):

        if "user" in message.content:
            scope = 'user'
            output = f"Details for [userID] removed from {str(message.guild)} - {str(message.channel)}"

        elif "channel" in message.content:
            scope = 'channel'
            output = f"All details for channel **{str(message.channel)}** removed from **{str(message.guild)}** by [userID]"

        elif "server" in message.content:
            scope = 'server'
            output = f"All details for all channels removed from **{str(message.guild)}** by [userID]"

        else:
            return

        dbhelpers.delete_content(message, scope, self.dbpath)
        return output

    def errorText(self, message, error):
        content = f'''Time: {datetime.datetime.now()}
Message: {message.clean_content}
Server: {message.guild}
Channel: {message.channel}
Author: {message.author}
Error: 
{error}'''
        send_error_message(content)


def runner(token, me, dbpath):
    """Helper function to run. Handles connection reset errors by automatically running again."""
    bot = None
    while True:
        try:
            bot = DicecordBot(token, me, dbpath)
            bot.startBot()
            bot.client.run(bot.token)
        except:
            tb = traceback.format_exc()
            send_error_message(f'Potential disconnect\n\n{tb}')
            if bot:
                bot.loop.close()
            checkConnection()
        if bot:
            bot.loop.close()


def checkConnection(host='8.8.8.8', port=53, timeout=53):
    # Try to connect to google
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            send_error_message("Reconnected")
            break
        except:
            send_error_message(f"No Connection still at {datetime.datetime.now()}")
            time.sleep(300)


if __name__ == '__main__':
    # get dbpath from sys args
    dbpath = ''
    runner(token, saver, dbpath)
