#Character object

import random

class Character:
    def __init__(self, ID):
        '''
        Class for holding players, making their rolls and saving their last rolls
        '''
        #Some means of identifying user
        #Generally either numeric ID or discord username depending on bot versus client implementation
        self.ID = ID
        #results of last roll, starts blank
        self.last_roll = []
        
        self.goodMessages = ["The Lie cannot withstand your will, [userID]!",
                    "Reality is yours to command, [userID]!",
                    "You should take the beat, [userID].",
                    "Aren't I a good bot, [userID]?",
                    "[userID] is a conduit to the supernal!",
                    "Did you hack me, [userID]?",
                    "[userID], if you were still a sleeper the majesty of this action would have awoken you!"]
        self.badMessages = ["[userID]'s nimbus looks like a wet dishrag.",
                   "The lie constricts your potential, [userID].",
                   "Don't blame your bad luck on me, [userID]! I'm just a random number generator.",
                   "That was just a practice roll, right [userID]?",
                   "[userID] rolls like a diary farmer.",
                   "Ask for a dramatic failure [userID], you know you want to!",
                   "[userID], I hope that wasn't an important roll ...",
                   "[userID]'s watchtower called out to the wrong soul."]

    def roll_set(self, dice, rote=False, again=10, quiet=False):
        '''
        roll a hand of dice subject to supplied conditions
        dice: int, the number of dice to roll
        rote: boolean, a rote roll rerolls all failed dice once
        again: int, which die faces explode
        quiet: Boolean about whether quiet mode will be used
        Returns a list of strings stating each die result and then total successes
        If quiet mode, returns a one element list that displays returns total successes and result of each die.
        '''
        
        # Check that more than 1 die selected
        if dice < 1:
            return ['Select at least 1 die.']

        # self.last_roll field collects the value of each rolled die
        # initialised to blank here, will be set in each self.roll_die call
        self.last_roll = []
        
        # successes collector variable 
        successes = 0
        
        # fail collector in case it is a rote
        fails = []

        
        for die in range(0,dice):
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
                successes += self.roll_die(again, rote_reroll = True)

        # send message
        messages = []
        
        if not quiet:
            # add all messages if quiet mode
            messages.extend(self.last_roll)

        else:
            # add a summary message
            out = self.ID + " rolled " + str(dice) + " dice and got " + str(successes) + " successes."
            for message in self.last_roll:
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
            messages.append("Total Successes for " + self.ID + " : " + str(successes))
        
        # check for positive or nagative message
        if successes == 0:
            messages.append(self.bot_message("bad"))
        elif successes >= 5:
            messages.append(self.bot_message("good"))
        
        return messages
        
    def bot_message(self, messagetype):
        '''
        Randomly sends a positive/negative message with very good or very bad rolls
        :param type: "good" or "bad"
        :return: none
        '''
        if messagetype == 'good':
                out = random.choice(self.goodMessages)
        else:
                out = random.choice(self.badMessages)

        return out.replace("[userID]", self.ID)
            
    def roll_die(self, again = 10, explode_reroll = False, rote_reroll = False):
        '''
        Rolls a single die, calculates number of successes
        Also updates the last_roll attribute with each roll result
        Handles explosions and gives custom last_roll text for rote/explosions
        '''
        value = random.randrange(1, 11)
    
        #recording value, adds details for rote/reroll
        if explode_reroll and rote_reroll:
            self.last_roll.append(self.ID + " rolled rote exploded die: " + str(value))
        elif explode_reroll:
            self.last_roll.append(self.ID + " rolled exploded die: " + str(value))
        elif rote_reroll:
            self.last_roll.append(self.ID + " rolled rote die: " + str(value))
        else:
            self.last_roll.append(self.ID + " rolled " + str(value))

        #checks for success/explosions
        if value >= again:
            #Exploding!
            return 1 + self.roll_die(again, True, rote_reroll)
        elif value >= 8:
            return 1
        else:
            return 0
    
    def roll_special(self):
        '''
        Rolls a single die, successes are not counted and last_roll not updated
        '''
        value = random.randrange(1, 11)
        return self.ID + " rolled a " + str(value) + "!"

    def roll_chance(self):
        '''
        Rolls a chance die.
        '''
        #make roll by choosing random bumber between 1 and 10
        value = random.randrange(1, 11)

        #clear last roll and append chance die result
        self.last_roll = []
        self.last_roll.append("chance die: " + str(value))

        #Give value
        messages = [self.ID + "chance rolled " + str(value)]

        ##check if failure, botch or success
        if value == 10:
            messages.append(self.ID + " got a success!")
            messages.append(self.bot_message("good"))
        elif value == 1:
            messages.append(self.ID + " botched!")
            messages.append(self.bot_message("bad"))
        else:
            messages.append(self.ID + " failed!")
            messages.append(self.bot_message("bad"))

        #Give result
        return messages

    def get_last_roll(self):
        #used for getting results of last roll made
        if self.last_roll == []:
            return [self.ID + " has no previous rolls."]
        return self.last_roll
