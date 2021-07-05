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
from __future__ import unicode_literals

import os
from asyncio import get_running_loop
from functools import partial
from random import randint
from urllib.parse import urlparse

import aiofiles
import aiohttp
import ffmpeg
import youtube_dl
from pyrogram import filters

from DaphneRobot import app, arq
from DaphneRobot.core.decorators.errors import capture_err
from DaphneRobot.utils.http import get
from DaphneRobot.utils.pastebin import paste

__MODULE__ = "Music"
__HELP__ = """/ytmusic [link] To Download Music From Various Websites Including Youtube. [SUDOERS]
/saavn [query] To Download Music From Saavn.
/deezer [query] To Download Music From Deezer.
/lyrics [query] To Get Lyrics Of A Song."""

is_downloading = False


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def download_youtube_audio(url: str, m=0):
    global is_downloading
    with youtube_dl.YoutubeDL(
        {
            "format": "bestaudio",
            "writethumbnail": True,
            "quiet": True,
        }
    ) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if int(float(info_dict["duration"])) > 600:
            is_downloading = False
            return []
        ydl.process_info(info_dict)
        audio_file = ydl.prepare_filename(info_dict)
        basename = audio_file.rsplit(".", 1)[-2]
        if info_dict["ext"] == "webm":
            audio_file_opus = basename + ".opus"
            ffmpeg.input(audio_file).output(
                audio_file_opus, codec="copy", loglevel="error"
            ).overwrite_output().run()
            os.remove(audio_file)
            audio_file = audio_file_opus
        thumbnail_url = info_dict["thumbnail"]
        thumbnail_file = (
            basename
            + "."
            + get_file_extension_from_url(thumbnail_url)
        )
        title = info_dict["title"]
        performer = info_dict["uploader"]
        duration = int(float(info_dict["duration"]))
    return [title, performer, duration, audio_file, thumbnail_file]


@app.on_message(filters.command("ytmusic"))
@capture_err
async def music(_, message):
    global is_downloading
    if len(message.command) != 2:
        return await message.reply_text(
            "/ytmusic needs a link as argument"
        )
    url = message.text.split(None, 1)[1]
    if is_downloading:
        return await message.reply_text(
            "Another download is in progress, try again after sometime."
        )
    is_downloading = True
    m = await message.reply_text(
        f"Downloading {url}", disable_web_page_preview=True
    )
    try:
        loop = get_running_loop()
        music = await loop.run_in_executor(
            None, partial(download_youtube_audio, url, message)
        )
        if not music:
            await m.edit("Too Long, Can't Download.")
        (
            title,
            performer,
            duration,
            audio_file,
            thumbnail_file,
        ) = music
    except Exception as e:
        is_downloading = False
        return await m.edit(str(e))
    await message.reply_audio(
        audio_file,
        duration=duration,
        performer=performer,
        title=title,
        thumb=thumbnail_file,
    )
    await m.delete()
    os.remove(audio_file)
    os.remove(thumbnail_file)
    is_downloading = False


# Funtion To Download Song
async def download_song(url):
    song_name = f"{randint(6969, 6999)}.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return
            f = await aiofiles.open(song_name, mode="wb")
            await f.write(await resp.read())
            await f.close()
    return song_name


# Jiosaavn Music


@app.on_message(filters.command("saavn") & ~filters.edited)
@capture_err
async def jssong(_, message):
    global is_downloading
    if len(message.command) < 2:
        return await message.reply_text(
            "/saavn requires an argument."
        )
    if is_downloading:
        return await message.reply_text(
            "Another download is in progress, try again after sometime."
        )
    is_downloading = True
    text = message.text.split(None, 1)[1]
    m = await message.reply_text("Searching...")
    try:
        songs = await arq.saavn(text)
        if not songs.ok:
            await m.edit(songs.result)
            is_downloading = False
            return
        sname = songs.result[0].song
        slink = songs.result[0].media_url
        ssingers = songs.result[0].singers
        await m.edit("Downloading")
        song = await download_song(slink)
        await m.edit("Uploading")
        await message.reply_audio(
            audio=song,
            title=sname,
            performer=ssingers,
        )
        os.remove(song)
        await m.delete()
    except Exception as e:
        is_downloading = False
        return await m.edit(str(e))
    is_downloading = False


# Deezer Music


@app.on_message(filters.command("deezer") & ~filters.edited)
@capture_err
async def deezsong(_, message):
    global is_downloading
    if len(message.command) < 2:
        return await message.reply_text(
            "/deezer requires an argument."
        )
    if is_downloading:
        return await message.reply_text(
            "Another download is in progress, try again after sometime."
        )
    is_downloading = True
    text = message.text.split(None, 1)[1]
    m = await message.reply_text("Searching...")
    try:
        songs = await arq.deezer(text, 1, 9)
        if not songs.ok:
            await m.edit(songs.result)
            is_downloading = False
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        await m.edit("Downloading")
        proxy = "http://52.187.67.188:5000"
        try:
            song = await download_song(
                f"{proxy}/mirror?url={url}.mp3"
            )
        except Exception:
            song = await download_song(url)
        if not song:
            song = await download_song(url)
        await m.edit("Uploading")
        await message.reply_audio(
            audio=song,
            title=title,
            performer=artist,
        )
        os.remove(song)
        await m.delete()
    except Exception as e:
        is_downloading = False
        return await m.edit(str(e))
    is_downloading = False
    try:
        await get(f"{proxy}/remove")
    except Exception:
        pass


# Lyrics


@app.on_message(filters.command("lyrics"))
async def lyrics_func(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:**\n/lyrics [QUERY]")
    m = await message.reply_text("**Searching**")
    query = message.text.strip().split(None, 1)[1]
    song = await arq.lyrics(query)
    lyrics = song.result
    if len(lyrics) < 4095:
        return await m.edit(f"__{lyrics}__")
    lyrics = await paste(lyrics)
    await m.edit(f"**LYRICS_TOO_LONG:** [URL]({lyrics})")
