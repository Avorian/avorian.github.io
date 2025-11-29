import json
import logging
from pathlib import Path
from typing import List

from aiohttp import web


class OverlayServer:
    def __init__(self, host: str, port: int, index_path: Path):
        self.host = host
        self.port = port
        self.index_path = index_path
        self._app = web.Application()
        self._websockets: List[web.WebSocketResponse] = []
        self._runner = None
        self._site = None

    async def start(self) -> None:
        self._app.router.add_get("/", self.handle_index)
        self._app.router.add_get("/ws", self.handle_ws)
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()
        logging.info("Overlay server running at http://%s:%s", self.host, self.port)

    async def stop(self) -> None:
        for ws in list(self._websockets):
            await ws.close()
        if self._runner:
            await self._runner.cleanup()
        logging.info("Overlay server stopped")

    async def handle_index(self, request: web.Request) -> web.Response:
        if not self.index_path.exists():
            return web.Response(text="Overlay not found", status=404)
        return web.FileResponse(self.index_path)

    async def handle_ws(self, request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._websockets.append(ws)
        logging.info("Overlay client connected (%s active)", len(self._websockets))
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    logging.debug("Overlay ping: %s", msg.data)
        finally:
            self._websockets.remove(ws)
            logging.info("Overlay client disconnected (%s active)", len(self._websockets))
        return ws

    async def broadcast_event(self, event: str, payload: dict) -> None:
        if not self._websockets:
            return
        message = json.dumps({"event": event, "payload": payload})
        for ws in list(self._websockets):
            try:
                await ws.send_str(message)
            except Exception as exc:
                logging.warning("Failed to push overlay event: %s", exc)


__all__ = ["OverlayServer"]
