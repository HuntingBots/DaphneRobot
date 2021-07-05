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
from pyrogram import filters

from DaphneRobot import app
from DaphneRobot.core.decorators.errors import capture_err
from DaphneRobot.core.decorators.permissions import adminsOnly
from DaphneRobot.utils.dbfunctions import (delete_note, get_note,
                                   get_note_names, save_note)

__MODULE__ = "Notes"
__HELP__ = """/notes To Get All The Notes In The Chat.
/save [NOTE_NAME] To Save A Note (Can be a sticker or text).
/get [NOTE_NAME] To Get A Note.
/delete [NOTE_NAME] To Delete A Note."""


@app.on_message(
    filters.command("save") & ~filters.edited & ~filters.private
)
@adminsOnly("can_change_info")
async def save_notee(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        await message.reply_text(
            "**Usage:**\nReply to a text or sticker with /save [NOTE_NAME] to save it."
        )

    elif (
        not message.reply_to_message.text
        and not message.reply_to_message.sticker
    ):
        await message.reply_text(
            "__**You can only save text or stickers in notes.**__"
        )
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            return await message.reply_text(
                "**Usage**\n__/save [NOTE_NAME]__"
            )
        _type = "text" if message.reply_to_message.text else "sticker"
        note = {
            "type": _type,
            "data": message.reply_to_message.text.markdown
            if _type == "text"
            else message.reply_to_message.sticker.file_id,
        }
        await save_note(message.chat.id, name, note)
        await message.reply_text(f"__**Saved note {name}.**__")


@app.on_message(
    filters.command("notes") & ~filters.edited & ~filters.private
)
@capture_err
async def get_notes(_, message):
    _notes = await get_note_names(message.chat.id)

    if not _notes:
        await message.reply_text("**No notes in this chat.**")
    else:
        msg = f"List of notes in {message.chat.title}\n"
        for note in _notes:
            msg += f"**-** `{note}`\n"
        msg += "Use **/get note_name** to get a note."
        await message.reply_text(msg)


@app.on_message(
    filters.command("get") & ~filters.edited & ~filters.private
)
@capture_err
async def get_one_note(_, message):
    if len(message.command) < 2:
        await message.reply_text("**Usage**\n__/get [NOTE_NAME]__")
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            return await message.reply_text(
                "**Usage**\n__/get [NOTE_NAME]__"
            )
        _note = await get_note(message.chat.id, name)
        if not _note:
            await message.reply_text("**No such note.**")
        else:
            if _note["type"] == "text":
                await message.reply_text(
                    _note["data"], disable_web_page_preview=True
                )
            else:
                await message.reply_sticker(_note["data"])


@app.on_message(
    filters.command("delete") & ~filters.edited & ~filters.private
)
@adminsOnly("can_change_info")
async def del_note(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage**\n__/delete [NOTE_NAME]__"
        )
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await message.reply_text(
            "**Usage**\n__/delete [NOTE_NAME]__"
        )
    chat_id = message.chat.id
    deleted = await delete_note(chat_id, name)
    if deleted:
        await message.reply_text(
            f"**Deleted note {name} successfully.**"
        )
    else:
        await message.reply_text("**No such note.**")
