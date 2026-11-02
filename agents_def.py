"""Agent graph: a triage agent that hands off to billing, technical support and plan specialists."""

from pathlib import Path

from agents import Agent, ModelSettings, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

import config
import tools

PROMPTS = Path(__file__).parent / "prompts"


def _prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text()


def build_triage(env: dict) -> Agent:
    model = OpenAIChatCompletionsModel(
        model=env["LLM_MODEL"],
        openai_client=AsyncOpenAI(base_url=env["LLM_BASE_URL"], api_key=env["LLM_API_KEY"]),
    )
    settings = ModelSettings(temperature=config.TEMPERATURE)

    billing = Agent(
        name="Billing specialist",
        handoff_description="Bill amounts, explaining charges and payments.",
        instructions=_prompt("billing"),
        model=model,
        model_settings=settings,
        tools=[tools.verify_account, tools.get_bill, tools.explain_charge, tools.apply_credit],
    )
    support = Agent(
        name="Technical support specialist",
        handoff_description="Coverage, outages, service credits for outages, slow or dead lines, technician visits.",
        instructions=_prompt("support"),
        model=model,
        model_settings=settings,
        tools=[tools.verify_account, tools.check_outage, tools.run_line_diagnostic, tools.schedule_technician],
    )
    plans = Agent(
        name="Plan specialist",
        handoff_description="Changing, upgrading or downgrading plans.",
        instructions=_prompt("plans"),
        model=model,
        model_settings=settings,
        tools=[tools.verify_account, tools.get_bill, tools.change_plan],
    )
    return Agent(
        name="Triage",
        instructions=_prompt("triage"),
        model=model,
        model_settings=settings,
        handoffs=[billing, support, plans],
    )
