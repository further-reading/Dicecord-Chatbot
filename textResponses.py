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
Note that natural langauage commands also work, as long as the keywords are present and the ordering is maintained.
For example "Hello @Dicecord roll me 8 dice please" will also roll 8 dice
'''

helptext = '''**Commands must now include an @mention for the bot**
To make a roll type **@Dicecord *type* *n*** where *n* is the number of dice you want to roll and *type* is the type of roll.

**Example:**
@Dicecord roll 8
Rolls 8 dice. Not a rote, 10s explode!

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