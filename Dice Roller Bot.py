#By Roy Healy
#Discord bot for rolling dice
#Current features:
#   Dice rolls (loud or quiet)
#   Help messaging
#   Send details of last roll
    

import discord
import random
import time
from character import Character

client = discord.Client()
players = []

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
    

def check_player(author):
    '''
    Helper function that finds character object associated with a user.
    '''
    global players
    
    for char in players:
        if char.ID == author:
            return char
        
    #if no player by this name found, new object created and added to global list
    char = Character(author)
    players.append(char)
    return char

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content == "!!one":
        #roll a single die, no successes calculated and not added to roll history
        char = check_player(str(message.author))

        result = char.roll_special()

        #Module will always use self.ID, but {0.author.mention} works better for bot implementation
        out = result.replace(char.ID, "{0.author.mention}")
        await client.send_message(message.channel, out.format(message))

    elif message.content=="!!chance":
        #make a chance roll
        #check who is talking
        char = check_player(str(message.author))

        results = char.roll_chance()

        for result in results:
            #Module will always use self.ID, but {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))
        
    elif message.content.startswith('!!') or message.content.startswith('##'):
        #this will be one a main roll commands
        
        #check who is talking 
        char = check_player(str(message.author))
        
        #make roll
        results = parse_roll(char, message.content)
        
        for result in results:
            #Module will always use self.ID, but {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))
            time.sleep(0.5)


    elif message.content=='!last_roll':
        #used for getting results of last roll made by speaker
        
        #check who is talking
        char = check_player(str(message.author))
        
        for result in char.get_last_roll():
            #Module will always use self.ID, but {0.author.mention} works better for bot implementation
            out = result.replace(char.ID, "{0.author.mention}")
            await client.send_message(message.channel, out.format(message))


    elif message.content.startswith('!type'):
        #type help text
        #replies in PM
        await client.send_message(message.author, "!!roll: a normal roll")
        await client.send_message(message.author, "!!rote: a rote roll (failures rerolled once)")
        await client.send_message(message.author, "!!9again: 9s explode!")
        await client.send_message(message.author, "!!8again: 8s explode!")
        await client.send_message(message.author, "!!9againrote: 9s explode and failures are rerolled once!")
        await client.send_message(message.author, "!!8againrote: 8s explode and failures are rerolled once!")
        await client.send_message(message.author, "Example:")
        await client.send_message(message.author, "!!roll 8")
        await client.send_message(message.author, "Rolls 8 dice. Not a rotes, 10s explode!")
        await client.send_message(message.author, "!!9again 5")
        await client.send_message(message.author, "Rolls 5 dice, 9s and 10s explode!")
        await client.send_message(message.author, "To roll a chance die, write '!!chance'")
        await client.send_message(message.author, "To roll a single die, but not as part of an action, write '!!one'")
        await client.send_message(message.author, "For quiet mode use ## instead of !!")
        await client.send_message(message.author, "There is no quiet mode for '!!chance' or !'!!one'")
        

    elif message.content.startswith('!help'):
        #help text
        #replies in PM
        await client.send_message(message.author, "To make a roll type '!![type] n'")
        await client.send_message(message.author, "'n' is the number of dice you want to roll.")
        await client.send_message(message.author, "'!![type]' is the type of roll.")
        await client.send_message(message.author, "There are special commands for chance rolls or generic single dice roll.")
        await client.send_message(message.author, "Write'!type' to get a list of all valid roll types and commands.")
        await client.send_message(message.author, "For quiet mode, use ## instead.")
        await client.send_message(message.author, "In loud mode, the bot will return the value of one roll every 0.5 seconds before stating total successes.")
        await client.send_message(message.author, "In quiet mode it will return the results in a single line.")
        await client.send_message(message.author, "To get the die values for your last roll, type '!last_roll'")
        await client.send_message(message.author, "You can send commands in this private chat if you don't want to spam the channel.")
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run("Bot Token")
