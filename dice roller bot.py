#cwod dice roller
#By Roy Healy
#Discord bot for rolling dice
#Current features:
#   Dice rolls (loud or quiet)
#   Help messaging
#   Send details of last roll
    

import discord
import random
import time

client = discord.Client()
players = []

class Player:
    #character stats
    def __init__(self, player):
        '''
        Class for holding players, making their rolls and saving their last rolls
        '''
        #player name
        self.player = player
        #results of last roll
        self.last_roll = []

    def make_roll(self, message):
        '''
        Checks text for type of roll, makes that roll.
        '''
        #

        #get number from input
        try:
            indx = message.index(' ')
        except ValueError:
            #occurs when no space present
            return "Error: no space found."

        dice = message[indx + 1:]
        #remove some common extra characters
        dice = dice.replace(" ", "")
        dice = dice.replace(".", "")

        try:
            dice = int(dice)
        except ValueError:
            #unexcpected characters in string
            return "Error: dice number entered incorrectly"

        if message.startswith('roll '):
            #normal
            return self.roll_set(dice)
            
        elif message.startswith('rote '):
            #rote
            return self.roll_set(dice, rote=True)
            
        elif message.startswith('8again '):
            #8again
            #checks if "rote" mentioned in message
            return self.roll_set(dice, again = 8, rote="rote" in message)
            
        elif message.startswith('9again '):
            #9again
            #checks if "rote" mentioned in message
            return self.roll_set(dice, again = 9, rote="rote" in message)
        
        else:
            #unrecognized command
            return "Unrecognized command!"

    def roll_set(self, dice, rote=False, again = 10):
        '''
        roll a hand of dice subject to supplied conditions
        dice: int, the number of dice to roll
        rote: boolean, a rote roll rerolls all failed dice once
        again: int, which die faces explode
        Returns number of successes
        '''
        
        #self.last_roll field collects the value of each rolled die
        #initialised to blank here, will be set in each self.cwod_roll call
        self.last_roll = []
        
        #successes collector variable 
        successes = 0
        
        #fail collector in case it is a rote
        fails = []
        for die in range(0,dice):
            result = self.cwod_roll(again)
            if result == 0:
                #if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
                #add result to success counter
            else:
                #add the result to successes counter
                successes += result

        if rote:
            #if a rote all failed dice are rerolled once
            for die in fails:
                successes += self.cwod_roll(again, rote_reroll = True)
        return successes
            
    def cwod_roll(self, again = 10, explode_reroll = False, rote_reroll = False):
        '''
        Rolls a single die, calculates number of successes
        Also updates the last_roll attribute with each roll result
        Handles explosions and gives custom last_roll text for rote/explosions
        '''
        value = random.randrange(1, 11)
    
        #recording value, adds details for rote/reroll
        if explode_reroll and rote_reroll:
            self.last_roll.append("rote exploded die: " + str(value))
        elif explode_reroll:
            self.last_roll.append("exploded die: " + str(value))
        elif rote_reroll:
            self.last_roll.append("rote die: " + str(value))
        else:
            self.last_roll.append(str(value))

        #checks for success/explosions
        if value >= again:
            #Exploding!
            return 1 + self.cwod_roll(again, True, rote_reroll)
        elif value >= 8:
            return 1
        else:
            return 0
    

def check_player(author):
    '''
    Helper function that finds character object associated with a user.
    '''
    global players
    
    for char in players:
        if char.player == author:
            return char
    #if no player by this name found, new object created and added to global list
    char = Player(author)
    players.append(char)
    return char

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content == "!!one":
        #roll a single die, no successes calculated and not added to roll history
        value = random.randrange(1, 11)
        out = "{0.author.mention} rolled: " + str(value)
        await client.send_message(message.channel, out.format(message))

    elif message.content=="!!chance":
        #check who is talking
        char = check_player(str(message.author))

        #make roll by choosing random bumber between 1 and 10
        value = random.randrange(1, 11)
        char.last_roll.append("chance die: " + str(value))

        #Give value
        out = "{0.author.mention}  rolled " + str(value)
        await client.send_message(message.channel, out.format(message))

        ##check if failure, botch or success
        if value == 10:
            out = "{0.author.mention} got a success!"
        elif value == 1:
            out = "{0.author.mention} botched!"
        else:
            out = "{0.author.mention} failed!"

        #Give result
        await client.send_message(message.channel, out.format(message))
        
        
    elif message.content.startswith('!!') or message.content.startswith('##'):
        #this will be one of the main roll commands
        
        #check who is talking 
        char = check_player(str(message.author))
        
        #make roll
        results = char.make_roll(message.content[2:])
        
        #if unrecognized command somewhere it returns a string instead of a number
        if type(results) is str:
            out = "{0.author.mention} had an error: " + results
            await client.send_message(message.channel, out.format(message))
            return
        
        if message.content.startswith('!!'):
            #Using !! will give results of each die one by one every 0.5 seconds
            #Using ## will skip this part
            for die in char.last_roll:
                out = "{0.author.mention} rolls " + die
                await client.send_message(message.channel, out.format(message))
                time.sleep(0.5)
        
        out = "Total Successes for {0.author.mention}: " + str(results) + "!"
        await client.send_message(message.channel, out.format(message))


    elif message.content=='!last_roll':
        #used for getting results of last roll made by speaker
        
        #check who is talking
        char = check_player(str(message.author))
        
        for roll in char.last_roll:
            out = "{0.author.mention}  rolled " + roll
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
        await client.send_message(message.author, "In quiet mode it will only return total successes.")
        await client.send_message(message.author, "To get the die values for your last roll, type '!last_roll'")
        await client.send_message(message.author, "You can send commands in this private chat if you don't want to spam the channel.")
        

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run("bot token")
