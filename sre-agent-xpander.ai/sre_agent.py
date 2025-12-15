import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Optional, Any

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MultiMCPTools
from agno.tools.thinking import ThinkingTools
from dotenv import load_dotenv
from xpander_utils.sdk.adapters import AgnoAdapter

# set up logging
t_logger = logging.getLogger(__name__)

# look for any kubectl command and strip code fences
KUBECTL = re.compile(r"kubectl\s+(.+)", re.IGNORECASE)
FENCE   = re.compile(r"```[\s\S]*?```", re.MULTILINE)

class LocalKubectlTool(MultiMCPTools):
    name = "kubectl"

    def __init__(self) -> None:
        super().__init__([self.name], env={})
        # capture context once
        self.ctx = subprocess.run(
            ["kubectl","config","current-context"],
            capture_output=True, text=True, check=False
        ).stdout.strip()

    def kubectl(self, flags: str) -> str:
        # run kubectl with saved context
        cmd = ["kubectl"] + (["--context", self.ctx] if self.ctx else []) + flags.split()
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.stdout if p.returncode == 0 else p.stderr

class SREAgent:
    def __init__(self, adapter: AgnoAdapter) -> None:
        self.adapter = adapter
        self.agent: Optional[Agent] = None
        self.ktool = LocalKubectlTool()

    async def run(
        self,
        message: str,
        *,
        user_id: str,
        session_id: str,
        cli: bool = False
    ) -> Any:
        # initialize LLM agent if needed
        if not self.agent:
            self.agent = self.build_agent()

        # get AI response
        resp = await (
            self.agent.aprint_response(message, user_id, session_id)
            if cli
            else self.agent.arun(message, user_id=user_id, session_id=session_id)
        )

        # remove code fences
        clean = FENCE.sub(
            lambda m: "\n".join(m.group(0).splitlines()[1:-1]), resp.content
        )
        # search anywhere for kubectl
        m = KUBECTL.search(clean)
        if m:
            flags = m.group(1).splitlines()[0].strip()
            resp.content = self.ktool.kubectl(flags)
            t_logger.info("ran kubectl %s", flags)
        return resp

    def build_agent(self) -> Agent:
        # set up the Agno agent with kubectl tool
        prompt = self.adapter.get_system_prompt()
        instr = ([prompt] if isinstance(prompt, str) else list(prompt)) + [
            "When user asks about Kubernetes, reply with a kubectl command.",
            "Always run commands to fetch live data."
        ]
        return Agent(
            model=OpenAIChat(id="gpt-4o"),
            tools=[ThinkingTools(add_instructions=True), self.ktool],
            instructions=instr,
            storage=self.adapter.storage,
            markdown=True,
            add_history_to_messages=True
        )

async def _cli() -> None:
    load_dotenv()
    cfg = json.loads(Path("xpander_config.json").read_text())
    backend = await asyncio.to_thread(
        AgnoAdapter,
        agent_id=cfg["agent_id"], api_key=cfg["api_key"], base_url=cfg.get("base_url")
    )
    agent = SREAgent(backend)
    while True:
        text = input("➜ ").strip()
        if text.lower() in {"exit","quit"}:
            break
        print((await agent.run(text, user_id="cli", session_id="dev", cli=True)).content)

if __name__ == "__main__":
    asyncio.run(_cli())
