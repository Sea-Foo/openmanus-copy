
from src.prompt.toolcall import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from src.agent.react import ReActAgent
from src.schema import Message

class ToolCallAgent(ReActAgent):

    name: str = "toolcall"
    description: str = "an agent that can execute tool calls."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    async def think(self) -> bool:
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]
