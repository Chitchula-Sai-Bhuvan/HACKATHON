
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError

class BaseAgent:
    """
    Base class for all agents in the Agentic Bug Hunter framework.
    Enforces system prompts, tool whitelists, and schema validation.
    """
    ROLE: str = ""
    SYSTEM_PROMPT: str = ""
    ALLOWED_TOOLS: List[str] = []
    
    # Optional: Map tool names to actual functions for enforcement
    TOOL_REGISTRY: Dict[str, Any] = {}

    def __init__(self, name: str):
        self.name = name

    def initialize_reasoning(self):
        """Logs the agent's intent and constraints based on its system prompt."""
        print(f"\n---  [{self.name}] Reasoning Initialization ---")
        print(f"Role: {self.ROLE}")
        print(f"Constraints enforced: {len(self.ALLOWED_TOOLS)} tools authorized.")
        # Minimalist summary of system prompt for the trace
        summary = self.SYSTEM_PROMPT.strip().split('\n')[0]
        print(f"Intent: {summary}")
        print("------------------------------------------")

    def validate_input(self, data: Any, schema_class: Optional[type[BaseModel]] = None):
        """Ensures input matches the expected schema."""
        if schema_class:
            try:
                schema_class.model_validate(data)
                print(f" [{self.name}] Protocol: Input schema validated.")
            except ValidationError as e:
                print(f"[{self.name}] Protocol: Input validation error: {e}")
                raise ValueError(f"Invalid input to {self.name}: {e}")

    def validate_output(self, data: Any, schema_class: Optional[type[BaseModel]] = None):
        """Ensures output matches the expected schema."""
        if schema_class:
            try:
                if isinstance(data, list):
                    for item in data:
                        schema_class.model_validate(item)
                else:
                    schema_class.model_validate(data)
                print(f"[{self.name}] Protocol: Output schema validated.")
            except ValidationError as e:
                print(f" [{self.name}] Protocol: Output validation error: {e}")
                raise ValueError(f"Invalid output from {self.name}: {e}")

    def enforce_tool(self, tool_name: str):
        """Runtime check for tool authorization."""
        if tool_name not in self.ALLOWED_TOOLS:
            print(f"[{self.name}] SECURITY ALERT: Unauthorized tool usage ({tool_name})")
            raise RuntimeError(f"Tool {tool_name} not allowed for agent {self.name}")
        print(f" [{self.name}] Tool authorized: {tool_name}")

    def get_full_prompt(self, user_prompt: str) -> str:
        """Injects system prompt before execution logic."""
        return f"{self.SYSTEM_PROMPT.strip()}\n\nUser Message: {user_prompt}"

    async def call_llm(self, user_prompt: str, max_tokens: int = 512) -> str:
        """Helper to call the generative brain with agent's system prompt."""
        from abh.tools.llm_manager import llm_manager
        print(f"🧠 [{self.name}] Calling Generative Brain...")
        response = await llm_manager.generate_response(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_new_tokens=max_tokens
        )
        return response

    async def execute(self, *args, **kwargs):
        """Placeholder for primary agent logic."""
        raise NotImplementedError("Subclasses must implement execute()")
