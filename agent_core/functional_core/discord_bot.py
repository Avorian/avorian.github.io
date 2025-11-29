import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands

from ..thought_engine.router import ThoughtRouter
from ..thought_engine.schemas import OracleContext
from .obs_control import OBSController
from .overlay_server import OverlayServer


class OracleDiscordBot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        router: ThoughtRouter,
        target_channel_id: Optional[int],
        obs_controller: OBSController,
        overlay: Optional[OverlayServer] = None,
        **kwargs,
    ):
        intents = kwargs.pop("intents", discord.Intents.default())
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)

        self.router = router
        self.target_channel_id = target_channel_id
        self.obs = obs_controller
        self.overlay = overlay

    async def on_ready(self):
        logging.info("Logged in as %s (ID: %s)", self.user, self.user.id if self.user else "?")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.target_channel_id and message.channel.id != self.target_channel_id:
            return

        context = OracleContext(
            user=str(message.author),
            channel=getattr(message.channel, "name", None),
            game=None,
            message_id=message.id,
        )

        decision = await self.router.decide_response(message.content, context)
        await message.channel.send(decision.reply.text)

        if self.overlay:
            await self.overlay.broadcast_event("oracle_reply", {"text": decision.reply.text})

        await self._execute_actions(decision.actions)

    async def _execute_actions(self, actions):
        for action in actions:
            if action.tool_name == "obs_clip_last_n_seconds":
                seconds = int(action.args.get("seconds", 10))
                label = action.args.get("label", "")
                await self._run_blocking(self.obs.clip_last_n_seconds, seconds, label)
            elif action.tool_name == "obs_start_stream":
                await self._run_blocking(self.obs.start_stream)
            elif action.tool_name == "obs_stop_stream":
                await self._run_blocking(self.obs.stop_stream)
            else:
                logging.info("Unknown tool action requested: %s", action.tool_name)

    async def _run_blocking(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, fn, *args, **kwargs)


def build_bot(router: ThoughtRouter, channel_id: Optional[int], obs: OBSController, overlay: Optional[OverlayServer]):
    return OracleDiscordBot(command_prefix="!", router=router, target_channel_id=channel_id, obs_controller=obs, overlay=overlay)


__all__ = ["OracleDiscordBot", "build_bot"]
