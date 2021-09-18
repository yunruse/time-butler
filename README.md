# time-butler

<p align="center">
    Discord bot to help coordinate events across timezones
    <a href="https://discord.com/api/oauth2/authorize?client_id=885905884650274857&permissions=0&scope=bot%20applications.commands">
        <img src="https://img.shields.io/badge/Discord-Invite%20bot%20to%20server-5865F2"
            alt="Invite Discord bot to server"></a>
</p>

A Discord bot to help coordinate times across servers. Simply summon with `/when Tomorrow at 2pm`, or any other natural-language query (in almost any language, too!) and Time Butler will return with a response which displays correctly in all time zones.

If you want to use Discord's fancy time formats yourself, simply DM the bot with `Tuesday at 8:30pm EST` et cetera.

Also has a small `/format` command, in case you want to quickly grab uʍop ǝpᴉsdn or sᴍᴀʟʟ ᴄᴀᴘs or 𝕕𝕠𝕦𝕓𝕝𝕖-𝕤𝕥𝕣𝕦𝕔𝕜 text without having to tab into your browser. (Just be aware that screen-readers can't read this kinda text!)

If you want to run the bot yourself, grab Python 3.7, `pip install discord.py discord-py-slash-command dateparser`, add `oauth-token.txt` with the token to your bot user, and run `time-butler.py`.