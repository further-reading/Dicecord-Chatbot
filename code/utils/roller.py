import random
from utils import messaging
import re


class Roller:
    rolls = []
    goodMessages = messaging.goodDefault.copy()
    badMessages = messaging.badDefault.copy()
    paradoxFail = messaging.badParadox.copy()

    def __init__(self, splat='default', flavour=True):
        """
        Class for holding details of a player and making their rolls.
        Args:
            ID (str): discord ID of player
            splat (str): which gameline the player has set
            flavour (bool): whether flavour messaging is active
        """

        self.rolls = []
        self.splat = splat
        self.changeSplat(splat)
        self.flavour = flavour

    @classmethod
    def from_dict(cls, character_dict):
        return cls(
            splat=character_dict['splat'],
            flavour=character_dict['flavour'],
        )

    def changeSplat(self, splat):
        """
        Set flavour messaging for selected splat
        Args:
            splat (str): which gameline the player has set

        Returns (str): Partial message confirming that splat was set

        """
        if splat == 'mage':
            self.splat = 'mage'
            self.goodMessages =  messaging.goodDefault.copy() + messaging.goodMage.copy()
            self.badMessages = messaging.badDefault.copy() + messaging.badMage.copy()

            return "Splat set to Mage in "

        elif splat == 'default':
            self.splat = 'default'
            self.goodMessages = messaging.goodDefault.copy()
            self.badMessages = messaging.badDefault.copy()

        elif splat:
            return "No custom settings for " + splat + ". Messaging unchanged in "

    def roll_set(self, dice, rote=False, again=10, paradox=False):
        """
        Roll a set of dice
        Args:
            dice (int): amount of dice to roll
            rote (bool): whether this is a rote roll
            again (int): lowest number that is rerolled
            paradox (bool): whether this is a paradox roll

        Returns (list of str): roll messages to return
        """

        if dice < 1:
            return ['Select at least 1 die.']

        self.rolls = []
        successes = 0
        
        # fail collector in case it is a rote
        fails = []

        for die in range(0, dice):
            # roll each die
            result = self.roll_die(again)
            if result == 0:
                # if not a success adds entry to fail list for rote reroll
                fails += ["fail"]
            else:
                successes += result

        if rote:
            for die in fails:
                successes += self.roll_die(again, rote_reroll=True)

        messages = []

        # add a summary message
        out = f"[userID] rolled {str(dice)} dice and got **{str(successes)} success"
        if successes != 1:
            out += "es**."
        else:
            out += "**."
        for message in self.rolls:
            # find dice value
            value = re.search(r'\d{1,2}', message).group(0)
            if "exploded" in message:
                out += "(" + value + ")"
            elif "rote" in message:
                out += " Rote:" + value
            else:
                out += " " + value

        messages.append(out)
        
        # check for positive or negative message
        if self.flavour and not paradox:
            if successes == 0:
                messages.append(self.bot_message("bad"))
            elif successes >= 5:
                messages.append(self.bot_message("good"))
        elif self.flavour and paradox:
            if successes != 0:
                messages.append(self.bot_message("paradox"))
        
        return messages
        
    def bot_message(self, messagetype):
        """
        Sends a random positive/negative message with very good or very bad rolls
        Args:
            messagetype (str): type of messaging to add

        Returns (str): message to add
        """
        out = ''
        if messagetype == 'good':
                out = random.choice(self.goodMessages)
        elif messagetype == 'bad':
                out = random.choice(self.badMessages)
        elif messagetype == 'paradox':
            out = random.choice(self.paradoxFail)

        return out
            
    def roll_die(self, again=10, explode_reroll=False, rote_reroll=False):
        """
        Rolls a single die, calculates number of successes and updates self.rolls
        Args:
            again (int): lowest number to reroll
            explode_reroll (bool): whether it is a reroll of an exploded dice
            rote_reroll (bool): whether it is a reroll of a rote

        Returns (int): number of successes

        """

        value = random.randrange(1, 11)

        if explode_reroll and rote_reroll:
            self.rolls.append("[userID] rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.rolls.append("[userID] rolled exploded die: " + str(value))
        elif rote_reroll:
            self.rolls.append("[userID] rolled rote die: " + str(value))
        else:
            self.rolls.append("[userID] rolled " + str(value))

        # Checks for success/explosions
        if value >= again:
            # Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            return 1
        else:
            return 0
    
    @staticmethod
    def roll_special():
        """
        Roll a single die
        Returns (str): Result of roll
        """
        value = random.randint(1, 10)
        return "[userID] rolled a " + str(value) + "!"

    def roll_chance(self, paradox=False):
        """
        Rolls a chance die
        Returns (list of str): Messages to send
        """
        value = random.randint(1, 10)
        messages = ["[userID] chance rolled " + str(value)]

        # Check if failure, botch or success
        if value == 10:
            messages.append("[userID] got a success!")
            if self.flavour:
                if paradox:
                    messages.append(self.bot_message("paradox"))
                else:
                    messages.append(self.bot_message("good"))
        elif value == 1:
            messages.append("[userID] botched!")
            if self.flavour:
                if paradox:
                    messages.append(self.bot_message("good"))
                else:
                    messages.append(self.bot_message("bad"))
        else:
            messages.append("[userID] failed!")
            if self.flavour and not paradox:
                messages.append(self.bot_message("bad"))

        return messages

    def roll_initiative(self, modifier):
        value = random.randint(1, 10)
        result = value + modifier
        messages = [f"[userID]'s initiative is {result} ({modifier} + Roll:{value})"]
        if self.flavour:
            if value == 10:
                messages.append(self.bot_message("good"))
            elif value == 1:
                messages.append(self.bot_message("bad"))
        return messages
