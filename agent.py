"""Northwind Mobile customer care agent, served as an OpenAI-compatible chat endpoint."""

import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from agents import MaxTurnsExceeded, Runner, set_tracing_disabled

import config
from agents_def import build_triage

set_tracing_disabled(True)
ENV = config.require_env()
FALLBACK = "Sorry, I could not finish that request. Please try again or ask me to start over."


def _text(content) -> str:
    if isinstance(content, list):
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def _history(messages: list[dict]) -> list[dict]:
    return [
        {"role": m["role"], "content": _text(m.get("content"))}
        for m in messages
        if m.get("role") in ("system", "user", "assistant") and _text(m.get("content"))
    ]


def _completed_tools(items) -> list[dict]:
    calls, done = [], []
    for item in items:
        if item.type == "tool_call_item":
            raw = item.raw_item
            calls.append({"id": raw.call_id, "name": raw.name, "arguments": raw.arguments, "output": None})
        elif item.type == "tool_call_output_item":
            call_id = item.raw_item["call_id"] if isinstance(item.raw_item, dict) else item.raw_item.call_id
            for call in calls:
                if call["id"] == call_id:
                    call["output"] = item.output
    for call in calls:
        try:
            args = json.loads(call["arguments"] or "{}")
        except ValueError:
            args = {}
        try:
            result = json.loads(call["output"])
        except (TypeError, ValueError):
            result = {"raw": call["output"]}
        failed = isinstance(result, dict) and (result.get("ok") is False or "raw" in result)
        done.append({"id": call["id"], "name": call["name"], "arguments": args, "result": result, "error": failed})
    return done


async def _respond(messages: list[dict]) -> tuple[str, list[dict]]:
    triage = build_triage(ENV)
    try:
        result = await Runner.run(triage, _history(messages), max_turns=config.MAX_TURNS)
    except MaxTurnsExceeded:
        return FALLBACK, []
    return str(result.final_output or ""), _completed_tools(result.new_items)


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path not in ("/v1/chat/completions", "/chat/completions"):
            return self._send(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            messages = body["messages"]
        except (ValueError, KeyError):
            return self._send(400, {"error": "body must be JSON with a messages list"})
        try:
            content, tools_run = asyncio.run(_respond(messages))
        except Exception as exc:  # model or network failure: still answer
            content, tools_run = f"Sorry, something went wrong on our side ({type(exc).__name__}).", []
        self._send(200, {
            "object": "chat.completion",
            "model": ENV["LLM_MODEL"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "completed_tools": tools_run,
        })

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", config.PORT), Handler)
    print(f"listening on :{config.PORT}", flush=True)
    server.serve_forever()
