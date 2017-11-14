# By Roy Healy
# Discord bot for rolling dice


import discord
import time
from character import Character
import datetime
from xml.dom import minidom
from xml.etree.ElementTree import Element, ParseError
from xml.etree import ElementTree as etree
import threading
import logging

logging.basicConfig(level=logging.ERROR)

client = discord.Client()
servers = {}

typetext = '''**roll**: a normal roll
**rote**: a rote roll (failures rerolled once)
**9again**: 9s explode!
**8again**: 8s explode!
**noagain**: Nothing explodes!
**9againrote**: 9s explode and failures are rerolled once!
**8againrote**: 8s explode and failures are rerolled once!
**noagainrote**: Nothing explodes but failures are rerolled once!
Example:
@Dicecord roll 8
Rolls 8 dice. Not a rotes, 10s explode!
@Dicecord 9again 5
Rolls 5 dice, 9s and 10s explode!
To roll a chance die, write **chance**
To roll a single die, but not as part of an action, write **one**
'''

helptext = '''**Commands must now include an @mention for the bot**
To make a roll type **@Dicecord *type* *n*** where *n* is the number of dice you want to roll and *type* is the type of roll.

**Example:**
@Dicecord roll 8
Rolls 8 dice. Not a rotes, 10s explode!

There are special commands for chance rolls or generic single dice roll.
Write **type** to me here to get a list of all valid roll types and commands.
Regardless of mode, by default the bot will send flavour text if you get 0 successes or 5+ successes.
You can specify splat specific flavour text, for example you could set it so a Mage character gets Mage themed flavour text.
To do so write **@Dicecord splat *splat name***. For example: **@Dicecord splat mage** for Mage.
You can turn flavour text off by writing **@Dicecord flavour off** in the channel. You can turn it back on with **@Dicecord flavour on**.
The bot will remember these settings. To check at any time write **@Dicecord flavour check** or **@Dicecord splat check**.
Settings are channel based, not server based. For example, you can set your splat to Mage in #Mage channel, but other channels on that server will have default settings.
To delete these settings for your character, write **@Dicecord delete user** in the channel you want deleted.
You can also use **@Dicecord delete channel** and *@Dicecord server* to delete all players' settings in a specific channel or server, but please make sure other players are okay with you performing these actions!
Type **info** to me here to general bot information.'''

aboutText = '''Dicecord is a python based bot for rolling dice following the Chronicles of Darkness ruleset.
(c) Roy Healy. Distributed under GNU General Public License v3.0.
Built using Discord.py package and running on Python 3.6.
See https://github.com/further-reading/discord-dirceroller-bot for source code.'''


def parse_roll(player, message):
    """Checks text for type of roll, makes that roll."""

    message = message.replace('@' + client.user.name, '')
    message = message.strip()

    # Find number of dice in message
    # Done this way to avoid the 8 or 9 in a 8again or 9again command
    dice = ''
    index = 0
    for letter in message[index + 1:]:
        if letter.isdigit():
            dice += letter
        elif letter == ' ' and dice != '':
            # this would be the space after the dice number
            # allows for users to use digits elsewhere if doing a natural language command
            break

    if dice == '':
        return

    dice = int(dice)

    if dice >= 300:
        return ["Too many dice. Please roll less than 300."]

    if '8again' in message:
        return player.roll_set(dice, again=8, rote="rote" in message)

    elif '9again' in message:
        return player.roll_set(dice, again=9, rote="rote" in message)

    elif 'noagain' in message:
        # no again sets again to 11 so it is impossible to occur
        return player.roll_set(dice, again=11, rote="rote" in message)

    elif "rote" in message:
        return player.roll_set(dice, rote=True)

    elif 'roll' in message:
        return player.roll_set(dice)


def check_server(message):
    """Helper function that finds character object associated with a user."""
    # Users have a character object for each channel in each server.

    global servers
    # {serverID : {channelID : {playerID: [character, lastCommandTime], playerID2: [character, lastCommandTime], etc}}}

    server = message.server.id
    channel = message.channel.id
    author = message.author.id

    if str(message.server) == "Under the Black Flag":  # being lazy and setting my game to mage
        char = Character(author)
        char.changeSplat('mage')
        servers[server] = {channel: {author: [char, datetime.datetime.now()]}}
        return char

    if server in servers:
        # check if channel is known
        if channel in servers[server]:
            # check if player is known
            if author in servers[server][channel]:
                # update command time and return character
                servers[server][channel][author][1] = datetime.datetime.now()
                return servers[server][channel][author][0]

            else:  # if player not known make new entry
                char = Character(author)
                servers[server][channel][author] = [char, datetime.datetime.now()]
        else:  # make a new channel entry
            char = Character(author)
            servers[server][channel] = {author: [char, datetime.datetime.now()]}

    else:  # make new server entry
        char = Character(author)
        servers[server] = {channel: {author: [char, datetime.datetime.now()]}}
    return char


def set_splat(message):

    char = check_server(message)
    new_splat = message.content[7:].lower()
    if new_splat == "check":
        if char.splat:
            return "Splat is currently set to " + char.splat.upper() + " in server " + str(
                message.server) + " - " + str(message.channel)
        else:
            return "Splat is currently not set in server " + str(message.server) + " - " + str(message.channel)

    else:
        return char.changeSplat(new_splat) + str(message.server) + " - " + str(message.channel)


def set_flavour(message):
    char = check_server(message)
    setting = message.content[9:].lower()
    if 'off' in setting:
        char.flavour = False
        return "Flavour turned off in server " + str(message.server) + " - " + str(message.channel)

    elif 'on' in setting:
        char.flavour = True
        return "Flavour turned on in server " + str(message.server) + " - " + str(message.channel)

    elif 'check' in setting:
        if char.flavour:
            return "Flavour turned on in server " + str(message.server) + " - " + str(message.channel)
        else:
            return "Flavour turned off in server " + str(message.server) + " - " + str(message.channel)


def delete_content(message):
    check_server(message)
    if "user" in message.content:
        del servers[str(message.server)][str(message.channel)][str(message.author)]
        return "Details for " + str(message.author) + " removed from " + str(message.server) + " - " + str(
            message.channel)

    elif "channel" in message.content:
        del servers[str(message.server)][str(message.channel)]
        return "All user details for channel **" + str(message.channel) + "** removed from **" + str(
            message.server) + "** by {0.author.mention}"

    elif "server" in message.content:
        del servers[str(message.server)]
        return "All user details for all channels removed from **" + str(message.server) + "** by {0.author.mention}"


def save_details():
    """Save current server settings"""
    # remove characters who have not been used in more than 30 days
    # after the character loop it removes all empty channels
    # after channel loop it removes all empty servers
    for server in list(servers):
        for channel in list(servers[server]):
            for user in list(servers[server][channel]):
                timeDifference = datetime.datetime.now() - servers[server][channel][user][1]
                if timeDifference.days > 30:
                    del servers[server][channel][user]
            if not servers[server][channel]:
                del servers[server][channel]
        if not servers[server]:
            del servers[server]

    root = Element('root')
    for server in servers:
        serv = Element('server')
        root.append(serv)

        servername = Element('name')
        serv.append(servername)
        servername.text = server

        for channel in servers[server]:
            chan = Element('channel')
            serv.append(chan)

            channame = Element('name')
            chan.append(channame)
            channame.text = channel

            for user in servers[server][channel]:
                use = Element('user')
                chan.append(use)

                usename = Element('name')
                use.append(usename)
                usename.text = user

                splatname = Element('splat')
                use.append(splatname)
                splatname.text = servers[server][channel][user][0].splat

                flavname = Element('flavour')
                use.append(flavname)
                flavname.text = str(servers[server][channel][user][0].flavour)

                usetime = Element('time')
                use.append(usetime)
                usetime.text = str(servers[server][channel][user][1])

    # write file
    rough_string = etree.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    text = reparsed.toprettyxml(indent="  ")

    f = open("details.xml", 'w', encoding='utf-8')
    f.write(text)
    f.close()


def read_details():
    global servers
    servers = {}

    try:
        dom = etree.parse("details.xml")
    except ParseError:
        servers = {}
        return

    servs = dom.findall('server')

    for server in servs:
        servname = server.find('name').text
        servers[servname] = {}
        channels = server.findall('channel')

        for channel in channels:
            channelname = channel.find('name').text
            servers[servname][channelname] = {}
            users = channel.findall('user')

            for user in users:
                username = user.find('name').text
                lasttime = user.find('time').text
                lasttime = datetime.datetime.strptime(lasttime, "%Y-%m-%d %H:%M:%S.%f")
                splat = user.find('splat').text
                flavour = user.find('flavour').text

                servers[servname][channelname][username] = [Character(username, splat, bool(flavour)), lasttime]


def errorText(message, error):
    print('Time: ' + str(datetime.datetime.now()) +
          '\nError: ' + error +
          '\nMessage: ' + str(message.clean_content) +
          '\nServer: ' + str(message.server) +
          '\nChannel: ' + str(message.channel) +
          '\nAuthor: ' + str(message.author) +
          '\n------\n')


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # we do not want the bot to reply to other bots
    if message.author.bot:
        return

    command = message.content.lower()

    if not message.server:  # Private Message - message.server = None
        if 'type' in command:
            await client.send_message(message.author, typetext)

        elif 'help' in command:
            await client.send_message(message.author, helptext)

        elif 'info' in command:
            await client.send_message(message.author, aboutText)

        elif str(message.author) == ME and "save" in command:
            # allows me to ask for a save of current settings at any time
            save_details()
            await client.send_message(message.author, "Saved details")

        else:
            await client.send_message(message.author,
                                      "Write 'help' for help, 'info' for bot info or 'type' for list of roll types")
        return

    # we only want bot to respond to @mentions
    if "@Dicecord" not in message.clean_content:
        return

    if "one" in command:
        char = check_server(message)
        # roll a single die, no successes calculated

        result = char.roll_special()

        # {0.author.mention} works better for bot implementation
        out = result.replace(char.ID, "{0.author.mention}")
        await client.send_message(message.channel, out.format(message))

    elif "chance" in command:
        char = check_server(message)
        results = char.roll_chance()

        for result in results:
            # {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))

    elif 'roll' in command or 'again' in command or 'rote' in command:
        char = check_server(message)
        results = parse_roll(char, message.clean_content)

        if not results:  # will return None if error occurred
            errorText(message, "Input error")
            return

        for result in results:
            # {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            try:
                await client.send_message(message.channel, out.format(message))
            except discord.Forbidden:
                errorText(message, "Forbidden Error")
            except UnicodeEncodeError:
                errorText(message, "Unicode Error")
            except discord.errors.HTTPException:
                errorText(message, "HTTP Exception")

            time.sleep(1)

    elif 'splat' in command:
        out = set_splat(message)
        if out:
            await client.send_message(message.author, out)

    elif 'flavour' in command:
        out = set_flavour(message)
        if out:
            await client.send_message(message.author, out)

    elif "delete" in command:
        out = delete_content(message)
        if out:
            await client.send_message(message.channel, out.format(message))


def saver():
    """A loop that saves the dictionary once a day"""
    save_details()
    print('------')
    print(str(datetime.datetime.now()) + ' Details Saved')
    print('------')
    threading.Timer(86400, saver).start()


def runner(token):
    """Helper function to run. Handles connection reset errors by automatically running again."""
    read_details()
    saver()
    try:
        client.run(token)
    except ConnectionResetError:
        save_details()
        runner(token)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='COMMANDS CHANGED - PM "help" for new commands'))

runner(BOTTOKEN)