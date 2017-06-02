#By Roy Healy
#Discord bot for rolling dice
#Current features:
#   Dice rolls (loud or quiet)
#   Help messaging
#   Flavour text
    

import discord
import random
import time
from character import Character

client = discord.Client()
# Collects channel IDs and player IDs
# This is to allow for saving the splat used for messaging options
# {serverID : {playerID: char}}
servers = {}

def parse_roll(player, message):
        '''
        Checks text for type of roll, makes that roll.
        The module always returns lists os strings, so any error message will be returned as a list of one string.
        '''
        
        #get type of roll
        if message.startswith("!!"):
            quiet = False
        else:
            quiet = True
        
        #Check if formatted correctly and find where space is
        try:
            indx = message.index(' ')
        except ValueError:
            #occurs when no space present
            return [player.ID + " error: no space found."]

        #Find number of dice in message
        dice = message[indx + 1:]
        
        #remove some common extra characters
        dice = dice.replace(" ", "")
        dice = dice.replace(".", "")

        try:
            #should be left with Int in string form
            dice = int(dice)
        except ValueError:
            #Unexcpected characters in string
            return [player.ID + " error: dice number entered incorrectly"]

        #check roll type by checking what firt word after !! or ## is
        if message[2:].startswith('roll'):
            #normal
            return player.roll_set(dice, quiet=quiet)
            
        elif message[2:].startswith('rote'):
            #rote
            return player.roll_set(dice, rote=True, quiet=quiet)
            
        elif message[2:].startswith('8again'):
            #8again
            #checks if "rote" mentioned in message
            return player.roll_set(dice, again = 8, rote="rote" in message, quiet=quiet)
            
        elif message[2:].startswith('9again'):
            #9again
            #checks if "rote" mentioned in message
            return player.roll_set(dice, again = 9, rote="rote" in message, quiet=quiet)
        
        else:
            #unrecognized command
            return [player.ID + " error: Unrecognized Command!"]
    

def check_server(message):
    '''
    Helper function that finds character object associated with a user.
    Users have a seperate character object for each channel in each server.
    '''
    global servers
    # {serverID : {channelID : {playerID: character, playerID: character}}}
    # check if message server is known
    if message.server in servers:
            # check if channel is known
            if message.channel in servers[message.server]:
                    # check if player is known
                    if message.author in servers[message.server][message.channel]:
                            # return character
                            return servers[message.server][message.channel][message.author]
                    else: # if player not known make new entry
                            char = Character(str(message.author))
                            servers[message.server][message.author] = char
            else: #make a new channel entry
                    char = Character(str(message.author))
                    servers[message.server][message.channel] = {message.author:char}

    else: # make new server entry
            char = Character(str(message.author))
            servers[message.server] = {message.channel:{message.author : char}}
    return char

def set_splat(message):
        '''
        Allows user to set game type for flavour text.
        '''
        char = check_server(message)
        new_splat = message.content[7:].lower()
        if new_splat == "check":
                if char.splat:
                        return "Splat is currently set to " + char.splat.upper() + " in server " + str(message.server) + " - " + str(message.channel)
                else:
                        return "Splat is currently not set in server " + str(message.server) + " - " + str(message.channel)
                
        
        else:
                return char.changeSplat(new_splat) + str(message.server) + " - " + str(message.channel)

def set_flavour(message):
        '''
        Allows user to set game type for flavour text.
        '''
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
        else:
                return "Unknown command."

def delete_content(message):
        check_server(message)
        if "user" in message.content:
                del servers[message.server][message.channel][message.author]
                return "Details for " + str(message.author) + " removed from " + str(message.server) + " - " + str(message.channel)

        elif "channel" in message.content:
                del servers[message.server][message.channel]
                return "All user details for channel " + str(message.channel) + " removed from " + str(message.server)

        elif "server" in message.content:
                del servers[message.server]
                return "All user details for all channels removed from " + str(message.server)

        else:
                return "Unkown Command"
        

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    char = check_server(message)
    if message.server == None:
            # Private Message
            if message.content.startswith('!type'):
                    await client.send_message(message.author,
                                  '''!!roll: a normal roll
!!rote: a rote roll (failures rerolled once)
!!9again: 9s explode!
!!8again: 8s explode!
!!9againrote: 9s explode and failures are rerolled once!
!!8againrote: 8s explode and failures are rerolled once!
Example:
!!roll 8
Rolls 8 dice. Not a rotes, 10s explode!
!!9again 5
Rolls 5 dice, 9s and 10s explode!
To roll a chance die, write '!!chance'
To roll a single die, but not as part of an action, write '!!one'
For quiet mode use ## instead of !!
There is no quiet mode for '!!chance' or !'!!one''')

            elif message.content.startswith('!help'):
                    #help text
                    #replies in PM
                    await client.send_message(message.author,
        '''To make a roll type *!![type] n* or *##[type] n* where'n' is the number of dice you want to roll and [type] is the type of roll.
There are special commands for chance rolls or generic single dice roll.
Write '!type' to me here to get a list of all valid roll types and commands.
Using !! specifies loud mode, using ## specifies quiet mode.
In loud mode, the bot will return the value of one roll every 0.5 seconds before stating total successes.
In quiet mode it will return the results in a single line.
Regardless of mode, by default the bot will send flavour text if you get 0 successes or 5+ successes.
You can specify splat specific flavour text, for example you could set it so a Mage character gets Mage themed flavour text. To do so write *!splat [splat name]*. Currently only valid for mage.
You can turn flavour text off by writing *!flavour off*. You can turn it back on with *!flavour on*.
The bot will remember these settings unless the bot server was reset. To check at any time write *!flavour check* or *!splat check*.
You need to edit these for every channel you are in. For example, you can set your splat to Vampire in #Vampire and Mage in #Mage within the same Discord server.
Such data will never be accessed or analaysed, but feel free to delete them at any time by writing *!delete user* in the channel you want deleted.
You can also use *!delete channel* and *!delete server* to delete all players' settings in a specific channel or server, but please make sure other players are okay with you performing these actions!
''')
            else:
                    #Give PM instructions
                    await client.send_message(message.author, "Write !help for help or !type for list of roll types")
           return
            
    # If not a PM or message from the bot, check for command
    if message.content == "!!one":
        #roll a single die, no successes calculated and not added to roll history

        result = char.roll_special()

        # {0.author.mention} works better for bot implementation
        out = result.replace(char.ID, "{0.author.mention}")
        await client.send_message(message.channel, out.format(message))

    elif message.content=="!!chance":
        #make a chance roll

        results = char.roll_chance()

        for result in results:
            # {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))
        
    elif message.content.startswith('!!') or message.content.startswith('##'):
        
        #make roll
        results = parse_roll(char, message.content)
        
        for result in results:
            # {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))
            time.sleep(0.5)

    elif message.content.startswith('!splat'):
        out = set_splat(message)
        if out:
                await client.send_message(message.author, out)

    elif message.content.startswith('!flavour'):
        out = set_flavour(message)
        if out:
                await client.send_message(message.author, out)

    elif message.content.startswith("!delete"):
            out = delete_content(message)
            if out:
                    await client.send_message(message.author, out)
            
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='!help for commands'))

client.run(BOT_TOKEN)
