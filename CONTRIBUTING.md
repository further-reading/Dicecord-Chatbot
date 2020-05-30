# Contributing to Dicecord-CoD
First off, thanks for taking the time to contribute! :)

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[What should I know before I get started?](#what-should-i-know-before-i-get-started)
  * [Packages](#packages)
  * [Design Decisions](#design-decisions)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
  
## Code Of Conduct
This project and everyone participating in it is governed by the [Dicecord(TM) Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
  
## What should I know before I get started?

### Packages
Dicecord is built using the [discord.py](https://github.com/Rapptz/discord.py) python package for discord bots. The current version in use is listed on the [readme][README.md]

### Design Decisions
Dicecord started as personal project for my personal game when I was still a pretty novice programmer, back when discord.py was also pretty new. As such there is plenty of code that does not adhere to best practices or use modern discord.py features. If you see code like this, it is unlikely to be a "design decision" but a relic of a more simpler age.

#### Another Player At The Table
One of the earliest feature requests I got was for the bot to feel like another player at the table. This request led to two features I consider core to Dicecord:   
1. The "flavour" messaging, where the bot comments on good and bad rolls.   
2. The natural language options for commands, where the bot will try to determine the roll from a plain english sentence.   
3. By default the bot doesn't use a prefix but is @mentioned to mimic speaking to another player. (this can be changed by players though)

The latter option is the main reason why I don't use the commands.ext module from discord.py.

### Game Specific
This bot is specifically for the [Chronicles of Darkness gameline by Onyx Path Publishing](http://theonyxpath.com/category/worlds/chroniclesofdarkness/). These rules are rolling a pool of D10 dice and counting successes on 8+. 10s explode, which means they count as a success and also get rolled again. There are additional options:

* The minimum number at which it explodes can change. This is called 8 again or 9 again.   
* Sometiems failied dice can be rerolled. This is known as a rote roll.  
* Penalties can be applied to a roll. If a penalty gives you a negative pool you roll a chance die. A chance die succeeds (and explodes) on 10 and causes a critical failure on a 1.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Dicecord. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report).

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). After you've determined [which repository](#atom-and-packages) your bug is related to, create an issue on that repository and provide the following information by filling in [the template](https://github.com/atom/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.md).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. 
* **Provide specific examples to demonstrate the steps**. Commands used, what your settings on your server are.
* **Give server, channel and user IDs**. To get IDs enable developer mode on your discord client, right click these areas and select copy ID.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**

Provide more context by answering these questions:

* **Can you reproduce the problem?** Try reproducing it locally, then try doing it in another server or channel.
* **Did the problem start happening recently**
