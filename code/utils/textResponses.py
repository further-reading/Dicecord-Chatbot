typetext = '''**rote**: a rote roll (failures rerolled once)
**9again**: 9s explode!
**8again**: 8s explode!
**noagain**: Nothing explodes!
**chance**: Roll a chance die.
**one**: Just roll a single die with no flavour/success messaging.
**paradox**: Use paradox flavour messaging (successes = bad)

Example:
@Dicecord-CoD roll 8
Rolls 8 dice. Not a rotes, 10s explode!
@Dicecord-CoD roll 9again 5
Rolls 5 dice, 9s and 10s explode!

You can chain commands when relevant.

@Dicecord-CoD roll 9again rote paradox 8
Roll 8 dice with 9again + rote. Use paradox messaging. 

Note that natural langauage commands can also work. It will figure out the amount to roll based on the following logic, where x is the amount of dice to roll:
1. Looks for a phrase like "roll x"
2. Looks for a phrase like "9again/8again/noagain x"
3. Takes first number after the @mention
4. Takes first number in message

Example
Hello @Dicecord-Cod can you roll 4 dice for me with 8again.
Rolls 4 dice with 8again
'''

helptext = '''**Commands must now include an @mention for the bot**
To make a roll type **@Dicecord-CoD roll [type] n** where *n* is the number of dice you want to roll and *type* is the type of roll.

**Example:**
@Dicecord-CoD roll 8
Rolls 8 dice. Not a rote, 10s explode!

There are special commands for chance rolls or generic single dice roll.
Write **type** to me here to get a list of all valid roll types and commands.

Regardless of mode, by default the bot will send flavour text if you get 0 successes or 5+ successes.
You can specify splat specific flavour text, for example you could set it so a Mage character gets Mage themed flavour text.
For more info, write **flavourhelp** to me here.

You can also change the prefix for your commands. Write **prefixhelp** here for more info.

Type **info** to me here to general bot information.
Support Dicecord on Patreon: https://www.patreon.com/further_reading'''

prefixHelp = '''"@Dicecord-Cod prefix new_prefix" will allow you to set a prefix for the bot to respond to. 
Note that the bot will still respond to @mentions when this is active.

To remove a prefix write "@Dicecord-Cod prefix reset"'''

flavText = '''To specify a splat write **@Dicecord-CoD splat *splat name***. For example: **@Dicecord-CoD splat mage** for Mage.
Currently only supports mage.
You can turn flavour text off by writing **@Dicecord-CoD flavour off** in the channel. You can turn it back on with **@Dicecord-CoD flavour on**.
The bot will remember these settings. To check at any time write **@Dicecord-CoD flavour check** or **@Dicecord-CoD splat check**.
Settings are channel based, not server based. For example, you can set your splat to Mage in #Mage channel, but other channels on that server will have default settings.
To delete these settings for your character, write **@Dicecord-CoD delete user** in the channel you want deleted.
You can also use **@Dicecord-CoD delete channel** and *@Dicecord-CoD server* to delete all players' settings in a specific channel or server, but please make sure other players are okay with you performing these actions!'''

aboutText = '''Dicecord-CoD is a python based bot for rolling dice following the Chronicles of Darkness ruleset.
(c) Roy Healy. Dicecord (TM). Distributed under GNU General Public License v3.0.
Built using Discord.py package and running on Python 3.6.
See https://github.com/further-reading/discord-dirceroller-bot for source code.
Join us on Discord! https://discordapp.com/invite/DRM9MT8
Support Dicecord on Patreon: https://www.patreon.com/further_reading'''