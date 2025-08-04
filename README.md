# voidnet

a python selfbot for discord built to automate, spam, and run wild with a user token.

> [!CAUTION]
> VOIDNET does not follow discor's TOS. using this script causes a very slight chance your ip to be temporarliy blocked by discord for 1-3 days if you abuse this too much (with spamming or something along those lines). during this time period, you can still use a vpn to access discord, but it is worth adding this warning.

---

## what the fuck is voidnet?

voidnet is a terminal-based selfbot, aka a script running on your **user** token instead of a proper bot account. it lets you automate actions, send messages, react to events, and generally be a pain in discord’s ass without needing a real bot.

it’s for those who want full control over user accounts, with all the dangerous, rule-breaking power that comes with it.

---

## requirements

* python 3.8+ (don’t run that garbage old shit)
* `requests` lib (`pip install requests`)
* a discord token (you or victim's)

---

## installation & usage

1. clone this shit:

   ```bash
   git clone https://github.com/s1deline/voidnet.git  
   cd voidnet  
   ```
2. install requests:

   ```bash
   pip install requests
   ```
3. run the bot with:

   ```bash
   python main.py
   ```
you can also just download a release version if you want it precompiled

---

## how it works (briefly)

voidnet uses user tokens to send requests to discord’s api and do everything a human would, but faster and without mercy. since it’s a selfbot, it can do shit normal bots can’t. but it also breaks tos on discord, so use at your own risk, or on a burner account.

---

## warnings & disclaimers

* selfbots are **against discord’s terms of service** and can get your account **banned.** only use on burner account or an account of a victim.
* this tool is for people who don’t give a fuck about rules and want to automate their user accounts.
* this is not made to use on other people! ignore that the last repo we posted was a discord token logger this totally has nothing to do with it! (it does)
* use responsibly (or don’t).