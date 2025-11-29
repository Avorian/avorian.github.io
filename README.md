# Oracle (Prototype)

Oracle is a local-first gaming and streaming copilot designed to run entirely on a single PC. It connects Discord, a local LLM runtime, OBS (via obs-websocket), and a lightweight overlay server so you can interact with the assistant in-game without relying on cloud compute.

## Architecture Overview

Oracle is split into two layers:

- **Thought Engine** (under `agent_core/thought_engine`): wraps LLM calls, defines schemas, and interprets user messages into replies plus optional tool actions.
- **Functional Core** (under `agent_core/functional_core`): bridges Discord, OBS, and the overlay server, and loads configuration.

```
Discord channel → ThoughtRouter → LLM (local) → reply + actions → Discord/OBS/Overlay
```

Current components:
- **Discord bot**: Listens in a dedicated channel and replies using the Thought Engine. Optional tool actions can trigger OBS.
- **LLM client**: Calls a local OpenAI-compatible endpoint on `localhost` by default. Cloud/hybrid modes are stubbed but configurable.
- **OBS control**: Connects to `obs-websocket` for starting/stopping streams or clipping the replay buffer. Falls back to logging if the client library is missing.
- **Overlay server**: Serves a minimal HTML page and WebSocket endpoint for pushing live events (e.g., Oracle replies).

## Repository Layout

- `agent_core/functional_core/` – Config loader, Discord bot bridge, OBS controller, overlay server.
- `agent_core/thought_engine/` – LLM client, response schemas, and routing/decision logic.
- `overlay/index.html` – Minimal overlay page that displays streamed Oracle messages.
- `config.example.yaml` – Sample configuration (copy to `config.yaml` and fill in secrets).
- `main.py` – Entry point to launch overlay + Discord bot.
- `TASKS.md` – Ongoing task list for prototype work.

## Setup

1. **Python environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Copy `config.example.yaml` to `config.yaml` and fill in values, or set environment variables:
     - `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`
     - `LLM_MODE`, `LLM_BASE_URL`, `LLM_TIMEOUT`, `LLM_MODEL`
     - `OBS_HOST`, `OBS_PORT`, `OBS_PASSWORD`
     - `OVERLAY_HOST`, `OVERLAY_PORT`
   - Default LLM mode is **local** and points at `http://127.0.0.1:1234/v1/chat/completions` (compatible with LM Studio or similar).

3. **Local LLM gateway**
   - Start your local LLM server (e.g., LM Studio in OpenAI-compatible mode) on the configured port.

4. **OBS WebSocket**
   - Enable obs-websocket (v5), set a password, and ensure the configured port is reachable.
   - The replay buffer should be configured if you want `clip_last_n_seconds` to save clips.

5. **Discord bot**
   - Create a bot in the Discord Developer Portal, invite it to your server, and note the target channel ID for in-game chat.

6. **Run Oracle**
   ```bash
   python main.py
   ```
   The overlay server will start (default `http://localhost:8765`), and the Discord bot will connect. Open `overlay/index.html` in OBS as a browser source to see replies.

## Known Limitations & Next Steps

- Steam game detection and per-game profiles are stubbed for future work.
- Session logging is limited to Python logs; structured game/session logs are not yet implemented.
- Cloud/hybrid LLM modes are placeholders; only local endpoints are active by default.
- OBS clipping assumes replay buffer configuration.

## Local-Only Defaults

All LLM calls target the configured localhost endpoint unless you explicitly change `llm.mode`. Avoid committing real tokens or passwords to the repository.
