# Northwind Mobile customer care agent

A chat agent for a mobile carrier, built with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
(`openai-agents` 0.24.0). A triage agent hands each customer to a billing, technical support or plan specialist.
Customers are verified with the last 4 digits of their account number and their billing ZIP code.

## Tools

| Tool | Used by | What it does |
| --- | --- | --- |
| `verify_account` | all specialists | Match last 4 digits and ZIP code to an account |
| `get_bill` | billing, plans | Current charges, total due and due date |
| `explain_charge` | billing | Explain one bill line |
| `apply_credit` | billing | Add a bill credit; capped per reason |
| `check_outage` | support | Known outages for a ZIP code |
| `run_line_diagnostic` | support | Status and signal check for one line |
| `change_plan` | plans | Preview or apply a plan change, with proration and early termination rules |
| `schedule_technician` | support | Book a morning or afternoon visit within 14 days |

## Run

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
export LLM_BASE_URL=https://api.example.com/v1 LLM_API_KEY=... LLM_MODEL=...
.venv/bin/python agent.py
```

The server listens on `0.0.0.0:$PORT`. `GET /health` returns `{"status": "ok"}`. `POST /v1/chat/completions`
(or `/chat/completions`) takes an OpenAI chat request with the full message history and returns a chat
completion plus a `completed_tools` list of every tool call made for the reply. No state is kept between requests.

## Layout

- `agent.py` HTTP server and run loop
- `agents_def.py` agents and handoffs
- `tools.py` tool names, descriptions and argument schemas
- `logic.py` business rules; `data.py` seeded accounts, plans and outages
- `prompts/` instructions for each agent
- `config.py` temperature, maximum turns, port

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `LLM_BASE_URL` | yes | OpenAI-compatible endpoint, ending in `/v1` |
| `LLM_API_KEY` | yes | API key for the endpoint |
| `LLM_MODEL` | yes | Model name |
| `PORT` | no | HTTP port, default 8080 |

## Sample accounts

| Account (last 4) | ZIP | Holder | Plan |
| --- | --- | --- | --- |
| 0931 | 94110 | Maria Alvarez | Plus |
| 5526 | 60614 | Devon Park | Basic |
| 3370 | 10027 | Priya Nair | Premium |
| 1175 | 73301 | Tom Becker | Plus |
