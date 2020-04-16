import asyncio
import discord

from typing import Any
from discord.utils import get
from datetime import datetime, timedelta

from redbot.core import Config, checks, commands
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.antispam import AntiSpam

from redbot.core.bot import Red

Cog: Any = getattr(commands, "Cog", object)


class Application(Cog):
    """
    Simple application cog, basically.
    **Use `[p]applysetup` first.**
    """

    __author__ = "saurichable"
    __version__ = "1.0.2"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, 5641654654621651651, force_registration=True
        )
        self.antispam = {}

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def apply(self, ctx: commands.Context):
        """Apply for free agency."""
        role_add = get(ctx.guild.roles, name="Free Agents")
        channel = get(ctx.guild.text_channels, name="free-agent-application")
        if ctx.guild not in self.antispam:
            self.antispam[ctx.guild] = {}
        if ctx.author not in self.antispam[ctx.guild]:
            self.antispam[ctx.guild][ctx.author] = AntiSpam([(timedelta(days=2), 1)])
        if self.antispam[ctx.guild][ctx.author].spammy:
            return await ctx.send("Uh oh, you're doing this way too frequently.")
        if role_add is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required role."
            )
        if channel is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required channel."
            )
        try:
            await ctx.author.send(
                "Let's start right away! You have maximum of 2 minutes for each question. Are you applying for free agency?"
            )
        except discord.Forbidden:
            return await ctx.send(
                "I don't seem to be able to DM you. Do you have closed DMs?"
            )
        await ctx.send(f"Okay, {ctx.author.mention}, I've sent you a DM.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.author.dm_channel

        try:
            position = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("What is your name?")
        try:
            name = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("rank?")
        try:
            age = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("Region?")
        try:
            timezone = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("Strengths?")
        try:
            days = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("Weaknesses?")
        try:
            hours = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send(
            "Please tell the teams about you."
        )
        try:
            experience = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        await ctx.author.send("What teams are you interested in?")
        try:
            reason = await self.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        embed = discord.Embed(color=await ctx.embed_colour(), timestamp=datetime.now())
        embed.set_author(name="New application!", icon_url=ctx.author.avatar_url)
        embed.set_footer(
            text=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})"
        )
        embed.title = (
            f"User: {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})"
        )
        embed.add_field(name="Name:", value=name.content, inline=True)
        embed.add_field(name="Rank:", value=age.content, inline=True)
        embed.add_field(name="Region:", value=timezone.content, inline=True)
        embed.add_field(name="Free Agent:", value=position.content, inline=True)
        embed.add_field(name="Strengths:", value=days.content, inline=True)
        embed.add_field(name="Weaknesses:", value=hours.content, inline=True)
        embed.add_field(
            name="About me:", value=experience.content, inline=False
        )
        embed.add_field(name="Teams interested in:", value=reason.content, inline=False)

        await channel.send(embed=embed)

        await ctx.author.add_roles(role_add)

        await ctx.author.send(
            "Your application has been sent to the Admins, thank you!"
        )
        self.antispam[ctx.guild][ctx.author].stamp()

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def applysetup(self, ctx: commands.Context):
        """Go through the initial setup process."""
        pred = MessagePredicate.yes_or_no(ctx)
        applicant = get(ctx.guild.roles, name="Free Agents")
        channel = get(ctx.guild.text_channels, name="free-agent-application")

        await ctx.send(
            "This will create required channel and role. Do you wish to continue? (yes/no)"
        )
        try:
            await self.bot.wait_for("message", timeout=30, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        if pred.result is False:
            return await ctx.send("Setup cancelled.")
        if applicant is None:
            try:
                await ctx.guild.create_role(
                    name="Free Agents", reason="Application cog setup"
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage roles."
                )
        if channel is None:
            await ctx.send(
                "Do you want everyone to see the applications channel? (yes/no)"
            )
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result is True:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        send_messages=False
                    ),
                    ctx.guild.me: discord.PermissionOverwrite(send_messages=True),
                }
            else:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    ),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                }
            try:
                await ctx.guild.create_text_channel(
                    "free-agent-application",
                    overwrites=overwrites,
                    reason="Application cog setup",
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage channels."
                )
        await ctx.send(
            "You have finished the setup! Please, move your new channel to the category you want it in."
        )

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def accept(self, ctx: commands.Context, target: discord.Member):
        """Accept a free agent application.
        <target> can be a mention or an ID."""
        applicant = get(ctx.guild.roles, name="Free Agents")
        role = MessagePredicate.valid_role(ctx)
        if applicant in target.roles:
            await ctx.send(f"What role do you want to accept {target.name} as?")
            try:
                await self.bot.wait_for("message", timeout=30, check=role)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            role_add = role.result
            await target.add_roles(role_add)
            await target.remove_roles(applicant)
            await ctx.send(f"Accepted {target.mention} as {role_add}.")
            await target.send(
                f"You have been accepted as {role_add} in {ctx.guild.name}."
            )
        else:
            await ctx.send(
                f"Uh oh. Looks like {target.mention} hasn't applied for anything."
            )

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def deny(self, ctx: commands.Context, target: discord.Member):
        """Deny a free agent applicant.
        <target> can be a mention or an ID"""
        applicant = get(ctx.guild.roles, name="Free Agents")
        if applicant in target.roles:
            await ctx.send("Would you like to specify a reason? (yes/no)")
            pred = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result is True:
                await ctx.send("Please, specify your reason now.")

                def check(m):
                    return m.author == ctx.author

                try:
                    reason = await self.bot.wait_for(
                        "message", timeout=120, check=check
                    )
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                await target.send(
                    f"Your application in {ctx.guild.name} has been denied.\n*Reason:* {reason.content}"
                )
            else:
                await target.send(
                    f"Your application in {ctx.guild.name} has been denied."
                )
            await target.remove_roles(applicant)
            await ctx.send(f"Denied {target.mention}'s application.")
        else:
            await ctx.send(
                f"Uh oh. Looks like {target.mention} hasn't applied for anything."
            )
