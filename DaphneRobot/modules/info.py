"""
MIT License



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
import os

from pyrogram import filters
from pyrogram.types import Message

from DaphneRobot import SUDOERS, app
from DaphneRobot.core.decorators.errors import capture_err
from DaphneRobot.modules.trust import get_spam_probability
from DaphneRobot.utils.dbfunctions import is_gbanned_user, user_global_karma

__MODULE__ = "Info"
__HELP__ = """
/info [USERNAME|ID] - Get info about a user.
/chat_info [USERNAME|ID] - Get info about a chat.
"""


async def get_user_info(user):
    user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    karma = await user_global_karma(user_id)
    spam_probab, n_messages = await get_spam_probability(user_id)
    isSpammer = (
        True
        if spam_probab > 70
        else False
        if spam_probab != 0
        else "Uncertain"
    )
    spam_probab = (
        str(round(spam_probab)) + " %"
        if spam_probab != 0
        else "Uncertain"
    )
    caption = f"""
**ID:** `{user_id}`
**DC:** {dc_id}
**Name:** {first_name}
**Username:** {("@" + username) if username else None}
**Mention:** {mention}
**Sudo:** {is_sudo}
**Karma:** {karma}
**Gbanned:** {is_gbanned}
**ARQ Spam Detection:**
    **Spammer:** {isSpammer}
    **Spam Probability:** {spam_probab}
    __Stats Of Last {n_messages} Messages.__
"""
    return [caption, photo_id]


async def get_chat_info(chat):
    chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type = chat.type
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[Link](t.me/{username})" if username else None
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    caption = f"""
**ID:** `{chat_id}`
**DC:** {dc_id}
**Type:** {type}
**Name:** {title}
**Username:** {("@" + username) if username else None}
**Mention:** {link}
**Members:** {members}
**Scam:** {is_scam}
**Restricted:** {is_restricted}
**Description:** {description}
"""
    return [caption, photo_id]


@app.on_message(filters.command("info"))
@capture_err
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]
    m = await message.reply_text("Processing")
    try:
        info_caption, photo_id = await get_user_info(user)
    except Exception as e:
        return await m.edit(str(e))
    if not photo_id:
        return await m.edit(
            info_caption, disable_web_page_preview=True
        )
    photo = await app.download_media(photo_id)
    await message.reply_photo(
        photo, caption=info_caption, quote=False
    )
    await m.delete()
    os.remove(photo)


@app.on_message(filters.command("chat_info"))
@capture_err
async def chat_info_func(_, message: Message):
    try:
        if len(message.command) > 2:
            return await message.reply_text(
                "**Usage:**/chat_info [USERNAME|ID]"
            )
        elif len(message.command) == 1:
            chat = message.chat.id
        elif len(message.command) == 2:
            chat = message.text.split(None, 1)[1]
        m = await message.reply_text("Processing")
        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(
                info_caption, disable_web_page_preview=True
            )
        photo = await app.download_media(photo_id)
        await message.reply_photo(
            photo, caption=info_caption, quote=False
        )
        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.reply_text(e)
        print(e)
        await m.delete()
