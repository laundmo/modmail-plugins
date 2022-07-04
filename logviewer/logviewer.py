from __future__ import annotations

import os

from typing import TYPE_CHECKING

import discord

from discord.ext import commands
from discord.utils import MISSING

from core import checks
from core.models import getLogger, PermissionLevel
from core.utils import strtobool

from .core.servers import AIOHTTPServer


if TYPE_CHECKING:
    from bot import ModmailBot

__version__ = "1.0.0"

logger = getLogger(__name__)


class Logviewer(commands.Cog, name="Log Viewer"):
    __doc__ = (
        "Log viewer plugin.\n\n"
        "This plugin is used to run a simple web server to view Modmail logs.\n"
        "Also checkout the [wiki](https://github.com/Jerrie-Aries/modmail-plugins/wiki/Log-Viewer-plugin).\n\n"
        f"**Version:**\n`{__version__}`"
    )

    def __init__(self, bot: ModmailBot):
        self.bot: ModmailBot = bot
        self.server: AIOHTTPServer = MISSING

    async def cog_load(self) -> None:
        if strtobool(os.environ.get("LOGVIEWER_AUTOSTART", True)):
            self.server = AIOHTTPServer(self.bot)
            await self.server.start()

    async def cog_unload(self) -> None:
        await self._stop_server()

    async def _stop_server(self) -> None:
        if self.server:
            await self.server.stop()
            self.server = MISSING

    @commands.group(name="logviewer", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.OWNER)
    async def logviewer(self, ctx: commands.Context):
        """
        Log viewer manager.
        """
        await ctx.send_help(ctx.command)

    @logviewer.command(name="start")
    @checks.has_permissions(PermissionLevel.OWNER)
    async def lv_start(self, ctx: commands.Context):
        """
        Starts the log viewer server.
        """
        if self.server:
            raise commands.BadArgument("Log viewer server is already running.")

        self.server = AIOHTTPServer(self.bot)
        await self.server.start()
        embed = discord.Embed(
            title="Start",
            color=self.bot.main_color,
            description="Log viewer server is now running.",
        )
        await ctx.send(embed=embed)

    @logviewer.command(name="stop")
    @checks.has_permissions(PermissionLevel.OWNER)
    async def lv_stop(self, ctx: commands.Context):
        """
        Stops the log viewer.
        """
        if not self.server:
            raise commands.BadArgument("Log viewer server is not running.")
        await self._stop_server()
        embed = discord.Embed(
            title="Stop", color=self.bot.main_color, description="Log viewer server is now stopped."
        )
        await ctx.send(embed=embed)

    @logviewer.command(name="info")
    @checks.has_permissions(PermissionLevel.OWNER)
    async def lv_info(self, ctx: commands.Context):
        """
        Shows information of the log viewer.
        """
        if not self.server:
            raise commands.BadArgument("Log viewer server is not running.")

        embed = discord.Embed(
            title="__Homepage__",
            color=self.bot.main_color,
            url=self.bot.config["log_url"].strip("/"),
        )
        embed.set_author(
            name="Log Viewer",
            icon_url=self.bot.user.display_avatar.url,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        main_deps = self.server.info()
        embed.description = f"Serving at port `{self.server.config.port}`.\n"
        embed.add_field(name="Dependencies", value=f"```py\n{main_deps}\n```")

        embed.set_footer(text=f"Version: v{__version__}")

        await ctx.send(embed=embed)


async def setup(bot: ModmailBot) -> None:
    await bot.add_cog(Logviewer(bot))
