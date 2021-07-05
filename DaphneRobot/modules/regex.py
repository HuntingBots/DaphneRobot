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
import re
import sre_constants

from pyrogram import filters

from DaphneRobot import app
from DaphneRobot.utils.filter_groups import regex_group

__MODULE__ = "Sed"
__HELP__ = "**Usage:**\ns/foo/bar"


DELIMITERS = ("/", ":", "|", "_")


@app.on_message(
    filters.regex(r"s([{}]).*?\1.*".format("".join(DELIMITERS))),
    group=regex_group,
)
async def sed(_, message):
    if not message.text:
        return
    sed_result = separate_sed(message.text)
    if message.reply_to_message:
        if message.reply_to_message.text:
            to_fix = message.reply_to_message.text
        elif message.reply_to_message.caption:
            to_fix = message.reply_to_message.caption
        else:
            return
        try:
            repl, repl_with, flags = sed_result
        except Exception:
            return

        if not repl:
            return await message.reply_text(
                "You're trying to replace... "
                "nothing with something?"
            )

        try:

            if infinite_checker(repl):
                return await message.reply_text("Nice try -_-")

            if "i" in flags and "g" in flags:
                text = re.sub(
                    repl, repl_with, to_fix, flags=re.I
                ).strip()
            elif "i" in flags:
                text = re.sub(
                    repl, repl_with, to_fix, count=1, flags=re.I
                ).strip()
            elif "g" in flags:
                text = re.sub(repl, repl_with, to_fix).strip()
            else:
                text = re.sub(
                    repl, repl_with, to_fix, count=1
                ).strip()
        except sre_constants.error:
            return

        # empty string errors -_-
        if len(text) >= 4096:
            await message.reply_text(
                "The result of the sed command was too long for \
                                                 telegram!"
            )
        elif text:
            await message.reply_to_message.reply_text(text)


def infinite_checker(repl):
    regex = [
        r"\((.{1,}[\+\*]){1,}\)[\+\*].",
        r"[\(\[].{1,}\{\d(,)?\}[\)\]]\{\d(,)?\}",
        r"\(.{1,}\)\{.{1,}(,)?\}\(.*\)(\+|\* |\{.*\})",
    ]
    for match in regex:
        status = re.search(match, repl)
        if status:
            return True
        else:
            return False


def separate_sed(sed_string):
    if (
        len(sed_string) >= 3
        and sed_string[1] in DELIMITERS
        and sed_string.count(sed_string[1]) >= 2
    ):
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == "\\":
                counter += 1

            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break

            counter += 1

        else:
            return None
        while counter < len(sed_string):
            if (
                sed_string[counter] == "\\"
                and counter + 1 < len(sed_string)
                and sed_string[counter + 1] == delim
            ):
                sed_string = (
                    sed_string[:counter] + sed_string[counter + 1 :]
                )

            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break

            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()
