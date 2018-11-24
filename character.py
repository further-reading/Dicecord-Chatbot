# Character object

import random

goodDefault = ["You should take the beat, [userID].",
                                 "Aren't I a good bot, [userID]?",
                                 "Did you hack me, [userID]?",
                                 "Masterfully done, [userID]!",
                                 "Don't let this luck go to waste, [userID]."]
badDefault = ["Don't blame your bad luck on me, [userID]! I'm just a random number generator.",
                                "That was just a practice roll, right [userID]?",
                                "[userID] rolls like a dairy farmer.",
                                "Ask for a dramatic failure [userID], you know you want to!",
                                "[userID], I hope that wasn't an important roll ..."]

badParadox = ["Don't blame your bad luck on me, [userID]! I'm just a random number generator.",
              "That was just a practice roll, right [userID]?",
              "The abyss does not react kindly to your manipulation, [userID].",
              "Let's make things interesting [userID], go for a manifestation!",
              "[userID], I hope that wasn't an important roll ..."]

class Character:
    def __init__(self, ID, splat='default', flavour=True):
        """Class for holding players, making their rolls and saving their last rolls"""

        self.ID = ID
        self.rolls = []
        self.splat= splat
        self.goodMessages =  goodDefault.copy()
        self.badMessages = badDefault.copy()
        self.paradoxFail = badParadox.copy()
        self.changeSplat(splat)
        self.flavour = flavour

    def changeSplat(self, splat):
        if splat == 'mage':
            self.splat = 'mage'
            self.goodMessages =  goodDefault.copy() + ["The Lie cannot withstand your will, [userID]!",
                                 "Reality is yours to command, [userID]!",
                                 "[userID] is a conduit to the supernal!",
                                 "[userID], if you were still a sleeper the majesty of this action would have awoken you!"]

            self.badMessages = badDefault.copy() + ["[userID]'s nimbus looks like a wet dishrag.",
                                "The lie constricts your potential, [userID].",
                                "[userID]'s watchtower called out to the wrong soul."]

            return "Splat set to Mage in "

        elif splat == 'default':
            self.splat = 'default'
            self.goodMessages = goodDefault.copy()
            self.badMessages = badDefault.copy()
            
        elif splat:
            return "No custom settings for " + splat + ". Messaging unchanged in "

    def roll_set(self, dice, rote=False, again=10, quiet=True, paradox=False):
        """roll a hand of dice subject to supplied conditions
        dice: int, the number of dice to roll
        rote: boolean, a rote roll rerolls all failed dice once
        again: int, which die faces explode
        quiet: Boolean about whether quiet mode will be used
        Returns a list of strings stating each die result and then total successes
        If quiet mode, returns a one element list that displays returns total successes and result of each die."""
        
        # Check that more than 1 die selected
        if dice < 1:
            return ['Select at least 1 die.']

        # self.last_roll field collects the value of each rolled die
        # initialised to blank here, will be set in each self.roll_die call
        self.rolls = []
        
        # successes collector variable 
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
                # add the result to successes counter
                successes += result

        if rote:
            # if a rote all failed dice are rerolled once
            for die in fails:
                successes += self.roll_die(again, rote_reroll=True)

        # send message
        messages = []
        
        if quiet:
            # add a summary message
            out = f"{self.ID} rolled {str(dice)} dice and got **{str(successes)}** success"
            if successes != 1:
                out += "es."
            else:
                out += "."
            for message in self.rolls:
                # find dice value
                value = ''.join(x for x in message[len(self.ID) + 1:] if x.isdigit())
                if "exploded" in message:
                    out += "(" + value + ")"
                elif "rote" in message:
                    out += " Rote:" + value
                else:
                    out += " " + value

            messages.append(out)

        # add total results message
        if not quiet:
            for roll in self.rolls:
                messages.append(roll)
            
            messages.append("Total Successes for " + self.ID + " : " + str(successes))
        
        # check for positive or nagative message
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
        """Sends a random positive/negative message with very good or very bad rolls"""
        if messagetype == 'good':
                out = random.choice(self.goodMessages)
        elif messagetype == 'bad':
                out = random.choice(self.badMessages)
        elif messagetype == 'paradox':
            out = random.choice(self.paradoxFail)

        return out.replace("[userID]", self.ID)
            
    def roll_die(self, again=10, explode_reroll=False, rote_reroll=False):
        """Rolls a single die, calculates number of successes
        Also updates the last_roll attribute with each roll result
        Handles explosions and gives custom last_roll text for rote/explosions"""

        value = random.randrange(1, 11)

        if explode_reroll and rote_reroll:
            self.rolls.append(self.ID + " rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.rolls.append(self.ID + " rolled exploded die: " + str(value))
        elif rote_reroll:
            self.rolls.append(self.ID + " rolled rote die: " + str(value))
        else:
            self.rolls.append(self.ID + " rolled " + str(value))

        # Checks for success/explosions
        if value >= again:
            # Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            return 1
        else:
            return 0
    
    def roll_special(self):
        """Rolls a single die, successes are not counted and last_roll not updated"""
        value = random.randrange(1, 11)
        return self.ID + " rolled a " + str(value) + "!"

    def roll_chance(self):
        """Rolls a chance die."""
        value = random.randrange(1, 11)
        messages = [self.ID + "chance rolled " + str(value)]

        # Check if failure, botch or success
        if value == 10:
            messages.append(self.ID + " got a success!")
            if self.flavour:
                messages.append(self.bot_message("good"))
        elif value == 1:
            messages.append(self.ID + " botched!")
            if self.flavour:
                messages.append(self.bot_message("bad"))
        else:
            messages.append(self.ID + " failed!")
            if self.flavour:
                messages.append(self.bot_message("bad"))

        return messages
