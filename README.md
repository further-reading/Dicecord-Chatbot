# Chronicles of Darkness Diceroller Bot for Discord
Python based diceroller bot for discord.

[![Discord Bots](https://discordbots.org/api/widget/319289665347911680.png)](https://discordbots.org/bot/319289665347911680?utm_source=widget)

## Use

To activate the bot go to https://discordapp.com/oauth2/authorize?client_id=319289665347911680&scope=bot&permissions=0

The bot will respond to any applicable commands made in the server that @mention it.

* **"[roll type] n"** - Rolls n dice based on conditions for [roll type]. Returns results in a single line. 
* **"one"** - Rolls a single 10-sided die and returns the value to the channel where the command was spoken.
* **"chance"** - Rolls a chance die, overwites the speaker's last_roll with result. Returns die result and states whether it was a botch, failure or success to the channel where the command was spoken.  

The bot will respond to natural language commands as long as the keyword is present and ordering is maintained. For example, if you write "Hello @Dicecord can you roll me 4 dice please" it is the same as writing "@Dicecord roll 4".

## Flavour Text
The bot will send flavour text in the case of 0 successes or 5+ successes. This falvour text can be themed to Chronicles of Darkness character types (a.k.a. splats) or disabled completely. Here are the commands to change these settings.
* **splat [type]** - Replace [type] with the splat type to get themed messaging. A confirmation will be sent as a DM.
* **splat check** - Check your current splat setting. Details will be sent as a DM.
* **flavour [on/off]** - Turn flavour text on or off. A confirmation will be sent as a DM.
* **flavour check** - Check your current flavour setting. Details will be sent as a DM.

You can also DM it the following commands to repeat these instructions.
* **"help"** - Replies with help text.  
* **"type"** - Replies to with the types of rolls available.  

## Information Saving
Splat and flavour settings are specific to each channel on your server. For example, if I have a #Mage channel and a #Vampire channel I could have different settings in each.

In addition, users can opt to delete their stored settings at any time. To do so write **!delete user** in the channel you want to delete information from. There are also commands to delete all players' settings from a channel or server, **!delete channel** or **!delete server**. Please make sure other players are okay with you deleting their settings before using it. If a character does not roll over the course of 30 days their settings will be automatically purged.

## Code Requirements
* Python 3.4.2+
* `Discord.py` API wrapper and its requirements. Github: [Rapptz](https://github.com/Rapptz/discord.py)
