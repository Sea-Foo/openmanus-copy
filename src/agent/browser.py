from typing import Optional

from src.agent.toolcall import ToolCallAgent
from src.prompt.browser import NEXT_STEP_PROMPT, SYSTEM_PROMPT

class BrowserAgent(ToolCallAgent):
    name: str = "browser"
    description: str = "A browser agent that can control a browser to accomplish tasks"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    async def get_browser_state(self) -> Optional[dict]:
        if not self._is_special_tool(name):
            return

    async def think(self) -> bool:
        pass
