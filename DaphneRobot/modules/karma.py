"""
MIT License

Copyright (c) 2021 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import re

from pyrogram import filters

from DaphneRobot import app
from DaphneRobot.core.decorators.errors import capture_err
from DaphneRobot.core.decorators.permissions import adminsOnly
from DaphneRobot.utils.dbfunctions import (alpha_to_int, get_karma,
                                   get_karmas, int_to_alpha,
                                   is_karma_on, karma_off, karma_on,
                                   update_karma)
from DaphneRobot.utils.filter_groups import (karma_negative_group,
                                     karma_positive_group)

__MODULE__ = "Karma"
__HELP__ = """[UPVOTE] - Use upvote keywords like "+", "+1", "thanks" etc to upvote a message.
[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.
/karma_toggle [ENABLE|DISABLE] - Enable or Disable Karma System In Your Chat.
Reply to a message with /karma to check a user's karma
Send /karma without replying to any message to chek karma list of top 10 users"""


regex_upvote = r"^(\+|\+\+|\+1|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍|\+\+ .+)$"
regex_downvote = r"^(-|--|-1|👎|-- .+)$"


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_positive_group,
)
@capture_err
async def upvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(
        chat_id, await int_to_alpha(user_id)
    )
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma + 1
        new_karma = {"karma": karma}
        await update_karma(
            chat_id, await int_to_alpha(user_id), new_karma
        )
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(
            chat_id, await int_to_alpha(user_id), new_karma
        )
    await message.reply_text(
        f"Incremented Karma of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=karma_negative_group,
)
@capture_err
async def downvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(
        chat_id, await int_to_alpha(user_id)
    )
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
        new_karma = {"karma": karma}
        await update_karma(
            chat_id, await int_to_alpha(user_id), new_karma
        )
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(
            chat_id, await int_to_alpha(user_id), new_karma
        )
    await message.reply_text(
        f"Decremented Karma Of {user_mention} By 1 \nTotal Points: {karma}"
    )


@app.on_message(filters.command("karma") & filters.group)
@capture_err
async def command_karma(_, message):
    chat_id = message.chat.id
    if not message.reply_to_message:
        m = await message.reply_text(
            "Analyzing Karma...Will Take 10 Seconds"
        )
        karma = await get_karmas(chat_id)
        if not karma:
            await m.edit("No karma in DB for this chat.")
            return
        msg = f"**Karma list of {message.chat.title}:- **\n"
        limit = 0
        karma_dicc = {}
        for i in karma:
            user_id = await alpha_to_int(i)
            user_karma = karma[i]["karma"]
            karma_dicc[str(user_id)] = user_karma
            karma_arranged = dict(
                sorted(
                    karma_dicc.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )
        if not karma_dicc:
            await m.edit("No karma in DB for this chat.")
            return
        for user_idd, karma_count in karma_arranged.items():
            if limit > 9:
                break
            try:
                user = await app.get_users(int(user_idd))
                await asyncio.sleep(0.8)
            except Exception:
                continue
            first_name = user.first_name
            if not first_name:
                continue
            username = user.username
            msg += f"**{karma_count}**  {(first_name[0:12] + '...') if len(first_name) > 12 else first_name}  `{('@' + username) if username else user_idd}`\n"
            limit += 1
        await m.edit(msg)
    else:
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(chat_id, await int_to_alpha(user_id))
        if karma:
            karma = karma["karma"]
            await message.reply_text(f"**Total Points**: __{karma}__")
        else:
            karma = 0
            await message.reply_text(f"**Total Points**: __{karma}__")


@app.on_message(filters.command("karma_toggle") & ~filters.private)
@adminsOnly("can_change_info")
async def captcha_state(_, message):
    usage = "**Usage:**\n/karma_toggle [ENABLE|DISABLE]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await karma_on(chat_id)
        await message.reply_text("Enabled karma system.")
    elif state == "disable":
        await karma_off(chat_id)
        await message.reply_text("Disabled karma system.")
    else:
        await message.reply_text(usage)
