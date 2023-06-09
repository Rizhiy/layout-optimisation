"""
Sends updates to a Telegram bot.

Usage:
>>> from tqdm.contrib.telegram import tqdm, trange
>>> for i in trange(10, token='{token}', chat_id='{chat_id}'):
...     ...

![screenshot](https://img.tqdm.ml/screenshot-telegram.gif)
"""
from __future__ import absolute_import

from os import getenv

from requests import Session
from tqdm.auto import tqdm as tqdm_auto
from tqdm.utils import _range

from .utils_worker import MonoWorker

__author__ = {"github.com/": ["casperdcl"]}
__all__ = ["TelegramIO", "tqdm_telegram", "ttgrange", "tqdm", "trange"]


class TelegramIO(MonoWorker):
    """Non-blocking file-like IO using a Telegram Bot."""

    API = "https://api.telegram.org/bot"

    def __init__(self, token, chat_id):
        """Creates a new message in the given `chat_id`."""
        super(TelegramIO, self).__init__()
        self.token = token
        self.chat_id = chat_id
        self.session = session = Session()
        self.text = self.__class__.__name__
        try:
            res = session.post(
                self.API + "%s/sendMessage" % self.token,
                data={"text": "`" + self.text + "`", "chat_id": self.chat_id, "parse_mode": "MarkdownV2"},
            )
        except Exception as e:
            tqdm_auto.write(str(e))
        else:
            self.message_id = res.json()["result"]["message_id"]

    def write(self, s):
        """Replaces internal `message_id`'s text with `s`."""
        if not s:
            s = "..."
        s = s.replace("\r", "").strip()
        if s == self.text:
            return  # avoid duplicate message Bot error
        self.text = s
        try:
            future = self.submit(
                self.session.post,
                self.API + "%s/editMessageText" % self.token,
                data={
                    "text": "`" + s + "`",
                    "chat_id": self.chat_id,
                    "message_id": self.message_id,
                    "parse_mode": "MarkdownV2",
                },
            )
        except Exception as e:
            tqdm_auto.write(str(e))
        else:
            return future


class tqdm_telegram(tqdm_auto):
    """
    Standard `tqdm.auto.tqdm` but also sends updates to a Telegram Bot.
    May take a few seconds to create (`__init__`).

    - create a bot <https://core.telegram.org/bots#6-botfather>
    - copy its `{token}`
    - add the bot to a chat and send it a message such as `/start`
    - go to <https://api.telegram.org/bot`{token}`/getUpdates> to find out
      the `{chat_id}`
    - paste the `{token}` & `{chat_id}` below

    >>> from tqdm.contrib.telegram import tqdm, trange
    >>> for i in tqdm(iterable, token='{token}', chat_id='{chat_id}'):
    ...     ...
    """

    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        token  : str, required. Telegram token
            [default: ${TQDM_TELEGRAM_TOKEN}].
        chat_id  : str, required. Telegram chat ID
            [default: ${TQDM_TELEGRAM_CHAT_ID}].

        See `tqdm.auto.tqdm.__init__` for other parameters.
        """
        if not kwargs.get("disable"):
            kwargs = kwargs.copy()
            self.tgio = TelegramIO(
                kwargs.pop("token", getenv("TQDM_TELEGRAM_TOKEN")),
                kwargs.pop("chat_id", getenv("TQDM_TELEGRAM_CHAT_ID")),
            )
        super(tqdm_telegram, self).__init__(*args, **kwargs)

    def display(self, **kwargs):
        super(tqdm_telegram, self).display(**kwargs)
        fmt = self.format_dict
        if fmt.get("bar_format", None):
            fmt["bar_format"] = fmt["bar_format"].replace("<bar/>", "{bar:10u}").replace("{bar}", "{bar:10u}")
        else:
            fmt["bar_format"] = "{l_bar}{bar:10u}{r_bar}"
        self.tgio.write(self.format_meter(**fmt))

    def clear(self, *args, **kwargs):
        super(tqdm_telegram, self).clear(*args, **kwargs)
        if not self.disable:
            self.tgio.write("")


def ttgrange(*args, **kwargs):
    """
    A shortcut for `tqdm.contrib.telegram.tqdm(xrange(*args), **kwargs)`.
    On Python3+, `range` is used instead of `xrange`.
    """
    return tqdm_telegram(_range(*args), **kwargs)


# Aliases
tqdm = tqdm_telegram
trange = ttgrange
