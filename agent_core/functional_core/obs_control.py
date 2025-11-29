import logging
from typing import Optional

try:
    from obswebsocket import obsws, requests
except ImportError:  # pragma: no cover - optional dependency at runtime
    obsws = None
    requests = None


class OBSController:
    def __init__(self, host: str, port: int, password: Optional[str]):
        self.host = host
        self.port = port
        self.password = password
        self.client = None

    def connect(self) -> None:
        if obsws is None:
            logging.warning("obs-websocket-py is not installed; OBS actions will be logged only.")
            return
        try:
            self.client = obsws(self.host, self.port, self.password)
            self.client.connect()
            logging.info("Connected to OBS at %s:%s", self.host, self.port)
        except Exception as exc:
            logging.error("Failed to connect to OBS: %s", exc)
            self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    def start_stream(self) -> None:
        if self.client is None or requests is None:
            logging.info("[OBS stub] start_stream")
            return
        try:
            self.client.call(requests.StartStream())
            logging.info("Triggered OBS start stream")
        except Exception as exc:
            logging.error("Failed to start stream: %s", exc)

    def stop_stream(self) -> None:
        if self.client is None or requests is None:
            logging.info("[OBS stub] stop_stream")
            return
        try:
            self.client.call(requests.StopStream())
            logging.info("Triggered OBS stop stream")
        except Exception as exc:
            logging.error("Failed to stop stream: %s", exc)

    def clip_last_n_seconds(self, seconds: int, label: str = "") -> None:
        if self.client is None or requests is None:
            logging.info("[OBS stub] clip_last_n_seconds: %s (%ss)", label, seconds)
            return
        try:
            # Assumes replay buffer is configured
            self.client.call(requests.TriggerReplayBuffer())
            self.client.call(requests.SaveReplayBuffer())
            logging.info("Saved OBS replay buffer for '%s' (%ss)", label, seconds)
        except Exception as exc:
            logging.error("Failed to clip replay buffer: %s", exc)


__all__ = ["OBSController"]
