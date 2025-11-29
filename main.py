import asyncio
import logging
from pathlib import Path

from agent_core.functional_core.config import load_config
from agent_core.functional_core.discord_bot import build_bot
from agent_core.functional_core.obs_control import OBSController
from agent_core.functional_core.overlay_server import OverlayServer
from agent_core.thought_engine.llm_client import LLMClient
from agent_core.thought_engine.router import ThoughtRouter


async def run():
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
    )

    llm_client = LLMClient(
        base_url=config.llm.base_url,
        mode=config.llm.mode,
        timeout=config.llm.timeout,
        model=config.llm.model,
    )
    router = ThoughtRouter(llm_client)

    obs = OBSController(config.obs.host, config.obs.port, config.obs.password)
    obs.connect()

    overlay_index = Path("overlay/index.html")
    overlay_server = OverlayServer(config.overlay.host, config.overlay.port, overlay_index)
    await overlay_server.start()

    bot = build_bot(router, config.discord.channel_id, obs, overlay_server)
    if not config.discord.token:
        logging.error("Discord bot token is not configured. Set DISCORD_BOT_TOKEN or config.yaml")
        return

    try:
        await bot.start(config.discord.token)
    finally:
        await overlay_server.stop()
        await llm_client.aclose()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
