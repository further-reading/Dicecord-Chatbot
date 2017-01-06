# Chronicles of Darkness Diceroller Bot for Discord
Python based diceroller bot for discord.

## Set up
1. Follow instructions on [Discord.py readme](https://github.com/Rapptz/discord.py/blob/master/README.md) to install discord.py python package.
2. Make a bot on [Discord Developer site](https://discordapp.com/developers/applications/me)
3. Copy the **Client ID** and the **Token** for your bot.  
![Bot settings](https://raw.githubusercontent.com/further-reading/discord-cwod-diceroller/master/token.png "Discord bot settings page")
4. In [the python code](https://github.com/further-reading/discord-cwod-diceroller/blob/master/dice%20roller%20bot.py) on the very last line replace "bot token" with the **Token** for your bot.   ```client.run("xxXXxXXxxX") ```  
5. Replace CLIENT ID in the following URL with your bot's **Client ID** ```https://discordapp.com/api/oauth2/authorize?client_id=CLIENT ID&scope=bot&permissions=0``` and open it in your browser.  
6. Add the bot to the servers you want to use it in.

## Use

To activate the bot run the python code in an appropiate client.
If running correctly, the bot will come online in the channel and the following will be printed to client console.

```py
Logged in as
BOTNAME
CLIENT ID
```
The bot will respond to any applicable commands made in the server or as a DM.  
"!help" - Sends DM to speaker with help text.  
"!type" - Sends DM to speaker with the types of rolls available.  
"!last_roll" - Sends the value of every die in the speaker's last roll to the channel where command was spoken.  
"!!one" - Rolls a single 10-sided die and returns the value to the channel where the command was spoken. Does not overwrite last_roll.  
"!!chance" - Rolls a chance die, overwites the speaker's last_roll with result. Returns die result and states whether it was a botch, failure or success to the channel where the command was spoken.  
"!![roll type] n" - Rolls n dice based on conditions for [roll type]. Returns each die result every 0.5 seconds to the channel where the command was spoken and then states total number of successes. Also overwrites the speaker's last_roll result.  
"##[roll type] n" - Quite mode roll. Just like "!![roll type] n" but it only gives total successes to channel. Also overwrites the speaker's last_roll result, so value of each die can be requested using "!last_roll".  

## Notes
The "!last_roll" command works by creating a list of every user that sends a command to the bot. I tend to start a new instance of the bot locally during a game and shut it down after so it isn't a big deal, but if you plan to have the bot run persistently or on multiple channels it might cause issues.

##Requirements
* Python 3.4.2+
* `Discord.py` API wrapper and its requirements. Github: [Rapptz](https://github.com/Rapptz/discord.py)
