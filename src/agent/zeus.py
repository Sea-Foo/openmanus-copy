from typing import Optional

from pydantic import Field, model_validator

from src.agent.browser import BrowserContextHelper
from src.agent.toolcall import ToolCallAgent
from src.config import config
from src.prompt.zeus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from src.tool import Terminate, ToolCollection
from src.tool.browser_use_tool import BrowserUseTool
from src.tool.python_execute import PythonExecute
from src.tool.str_replace_editor import StrReplaceEditor


class Zeus(ToolCallAgent):

    name: str = "Zeus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(), BrowserUseTool(), StrReplaceEditor(), Terminate()
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    browser_context_helper: Optional[BrowserContextHelper] = None

    @model_validator(mode="after")
    def initialize_helper(self) -> "Zeus":
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    async def think(self) -> bool:
        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name == BrowserUseTool().name
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )

        result = await super().think()

        self.next_step_prompt = original_prompt

        return result

    async def cleanup(self):
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
