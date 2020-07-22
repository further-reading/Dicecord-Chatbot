import discord
import time
import asyncio
import datetime
import socket
import traceback
import re
import sys

from utils.error_logger import send_error_message
from utils.tokens import saver, token
from utils import textResponses
from utils.roller import Roller
from utils.messaging import SPLATS
from utils.patreon_helper import get_credits
import dbhelpers


class PoolError(Exception):
    pass

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
        except:
            tb = traceback.format_exc()
            self.errorText(message, tb)
            self.errorText(message, f'Unknown error\n{tb}')

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
        if str(message.author) == self.me and "save-cod" in message.content.lower():
            # used to update server count on discord bot list
            await self.send(f'servers:{len(self.client.guilds)}', message)
            # sometimes activity goes away, use this as an opportunity to reset it
            await self.client.change_presence(activity=discord.Game(name='PM "help" for commands'))
            return

        if message.author.bot:
            return

        if not message.guild:  # Private Message - message.guild = None
            await self.pmCommands(message)
            return

        command = self.format_command(message)
        if not command:
            return

        out = None
        if ' roll ' in command:
            out = self.handle_roll(message, command)

        elif ' splat' in command or command.endswith(' splat'):
            out = self.set_splat(message)

        elif ' flavour ' in command:
            out = self.set_flavour(message)

        elif " delete " in command:
            out = self.delete_content(message)

        elif " prefix " in command or command.endswith(' prefix'):
            out = self.set_prefix(message)

        if out is not None:
            out = out.replace('[userID]', "{0.author.mention}")
            out = out.format(message)
            await self.send(out, message)

    def format_command(self, message):
        command = message.content.lower()
        prefix = dbhelpers.get_prefix(message, self.dbpath)
        if self.client.user in message.mentions:
            # always reply when @mentioned
            return command

        if prefix and command.startswith(prefix + ' '):
            return command.replace(prefix, '', 1)

    def handle_roll(self, message, command):
        """Checks text for type of roll, makes that roll."""
        if 'roll one' in command:
            return Roller.roll_special()

        flavour, splat = dbhelpers.get_flavour(message, self.dbpath)
        character = {'flavour': flavour, 'splat': splat}
        roller = Roller.from_dict(character)
        if "chance" in command:
            results = roller.roll_chance(paradox="paradox" in command)
            results = '\n'.join(results)
            return results

        else:
            again = self.get_again_amount(command)
            if 'roll pool' in command:
                try:
                    dice_amount = self.get_pool(command)
                    if dice_amount < 1:
                        # roll chance
                        results = [f'Calculated a pool of {dice_amount} dice - chance roll']
                        results += roller.roll_chance(paradox="paradox" in command)
                        results = '\n'.join(results)
                        return results

                except PoolError:
                    return 'Too many values, please only include 10 or fewer terms.'
            else:
                dice_amount = self.getDiceAmount(command)

            if dice_amount is None:
                # stop if no dice number found
                return

            if dice_amount >= 50:
                return "Too many dice. Please roll less than 50."
            else:
                results = roller.roll_set(
                    dice_amount,
                    again=again,
                    rote="rote" in command,
                    paradox="paradox" in command,
                )
                results = '\n'.join(results)
                return results

    def get_again_amount(self, command):
        again_term = re.search("(8|9|no)again", command)
        if again_term:
            again = again_term.group(0)
            if again == '8again':
                again = 8
            elif again == '9again':
                again = 9
            elif again == 'noagain':
                again = 11
        else:
            again = 10
        return again

    def getDiceAmount(self, messageText):
        """Gets the amount of dice to roll

        Args:
            messageText (str): text of message

        Returns (int or None): amount of dice to roll
        """

        if "roll" in messageText:
            # First check for message of the form roll x
            matched = re.search(r'\broll ([0-9]+\b)', messageText)
            if matched:
                return int(matched.group(1))

        again = re.search("(8|9|no)again", messageText)
        if again:
            again = again.group()
            # Second check for message of the form againTerm x
            matched = re.search(f'(?<=\\b{again} )[0-9]+\\b', messageText)
            if matched:
                return int(matched.group())
            else:
                messageText = messageText.replace(again, '')

        # Check for first number after @mention and then first number in message
        splitMessage = messageText.split(f'{self.client.user.id}')
        for message in splitMessage[::-1]:
            matched = re.search(r'\b\d+\b', message)
            if matched is not None:
                return int(matched.group())

    def get_pool(self, text):
        regex_1 = r'pool (-?\d{1,2})'
        regex_2 = r'([+-] ?\d{1,2})'
        numbers = re.findall(f'{regex_1}', text)
        numbers += re.findall(f'{regex_2}', text)
        if len(numbers) > 10:
            raise PoolError
        numbers = ''.join(numbers)
        pool = eval(numbers)
        return pool

    def set_prefix(self, message):
        if message.endswith('prefix'):
            # checking current prefixes
            pass
        new_prefix, server_wide = self.extract_prefix(message)
        if new_prefix:
            if new_prefix == 'reset':
                new_prefix = None
            dbhelpers.set_prefix(
                new_prefix,
                message,
                self.dbpath,
                server_wide,
            )
            if server_wide:
                output = f"Server Prefix changed by [userID] to **{new_prefix}** in server {message.guild}"
            else:
                output = f"Prefix changed by [userID] to **{new_prefix}** in server {message.guild} - #{message.channel}"
            return output

    def extract_prefix(self, message):
        # command of form 'prefix {new_prefix}'
        text = message.content
        prefix = re.search(r'prefix(?: server)? (\S+)', text)
        if prefix:
            prefix = prefix.group(1)
        return prefix, ' server ' in message.content

    def set_splat(self, message):
        """Allows user to set game type for flavour text."""

        if "check" in message.content.lower() or message.content.endswith('splat'):
            _, splat = dbhelpers.get_flavour(message, self.dbpath)
            if splat:
                return f"Splat for [userID] is currently set to {splat} in server {message.guild} - #{message.channel}"
            else:
                return f"Splat for [userID] is currently not set in server {str(message.guild)} - {str(message.channel)}"

        else:
            new_splat = self.find_splat(message.content.lower())
            if new_splat:
                dbhelpers.set_splat(message, new_splat, self.dbpath)
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
            patrons = get_credits()
            if patrons:
                content += f'\n\n**Special thanks to our Patreon patrons**\n```\n{patrons}\n```'

        elif 'prefix' in command:
            content = textResponses.prefixHelp

        else:
            content = "Write 'help' for help, 'info' for bot info, 'type' for list of roll types"

        await self.send(content, message)


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
            break
        except:
            send_error_message(f"No Connection still at {datetime.datetime.now()}")
            time.sleep(300)
    send_error_message("Reconnected")


if __name__ == '__main__':
    dbpath = sys.argv[1]
    try:
        dbhelpers.create_tables(dbpath)
    except dbhelpers.db.OperationalError:
        # table already exists
        pass
    runner(token, saver, dbpath)
