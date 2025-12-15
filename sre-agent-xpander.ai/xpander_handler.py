import asyncio
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Disable UNIX-only signal handlers on Windows 
import asyncio as _asyncio
_asyncio.AbstractEventLoop.add_signal_handler = lambda *a, **k: None

from xpander_utils.events import XpanderEventListener, AgentExecutionResult, AgentExecution
from xpander_utils.sdk.adapters import AgnoAdapter
from sre_agent import SREAgent

# Init 
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cfg = json.loads(Path("xpander_config.json").read_text())

# Management-API client
xp_adapter = asyncio.run(
    asyncio.to_thread(
        AgnoAdapter,
        agent_id=cfg["agent_id"],
        api_key=cfg["api_key"],
    )
)

agent = SREAgent(xp_adapter)

# Execution callback (forward only) 
async def handle_execution_request(task: AgentExecution) -> AgentExecutionResult:
    try:
        # Optional: register task for Xpander metrics
        await asyncio.to_thread(
            xp_adapter.agent.init_task,
            execution=task.model_dump()
        )

        resp = await agent.run(
            message=task.input.text,
            user_id=task.input.user.id,
            session_id=task.memory_thread_id,
            cli=False,
        )
        return AgentExecutionResult(result=resp.content, is_success=True)

    except Exception as exc:
        logger.exception("Error handling execution request")
        return AgentExecutionResult(result=str(exc), is_success=False)

#  Start SSE listener 
listener = XpanderEventListener(
    api_key         = cfg["api_key"],
    organization_id = cfg["org_id"],
    agent_id        = cfg["agent_id"],
    base_url        = cfg["base_url"],
)
listener.register(on_execution_request=handle_execution_request)
