import os
from typing import List, Dict, Optional
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMManager:
    """
    Singleton manager for interacting with Hugging Face Inference API.
    Provides a generative brain to the agents.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.api_token = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.model_id = os.getenv("HF_MODEL_ID")
        
        if not self.api_token:
            print("[LLMManager] No API token found (HF_TOKEN, OPENAI_API_KEY, or GROQ_API_KEY). LLM will be disabled.")
            self.client = None
            self._protocol = None
        else:
            # Detect protocol
            if self.api_token.startswith("hf_"):
                self._protocol = "huggingface"
                self.model_id = self.model_id or "HuggingFaceH4/zephyr-7b-beta"
                self.client = InferenceClient(model=self.model_id, token=self.api_token)
                print(f"[LLMManager] Initialized Hugging Face Inference Client ({self.model_id})")
            elif self.api_token.startswith("gsk_"):
                self._protocol = "groq"
                self.model_id = self.model_id or "llama-3.1-8b-instant"
                # We use httpx to call Groq/OpenAI compatible APIs to keep it lightweight
                self.client = "API_KEY_PRESENT" 
                print(f"[LLMManager] Initialized Groq-compatible Client ({self.model_id})")
            else:
                # Fallback to generic OpenAI compatible
                self._protocol = "openai"
                self.model_id = self.model_id or "gpt-3.5-turbo"
                self.client = "API_KEY_PRESENT"
                print(f"[LLMManager] Initialized OpenAI-compatible Client ({self.model_id})")
            
        self._initialized = True

    def set_token(self, token: str):
        """Allows setting the token at runtime if not in env."""
        # This method needs to be updated to handle different protocols if it's to be used.
        # For now, it's kept as is, assuming it's primarily for HF token re-initialization.
        # A more robust solution would involve re-running the protocol detection logic.
        self.api_token = token
        if self.api_token.startswith("hf_"):
            self._protocol = "huggingface"
            self.client = InferenceClient(model=self.model_id, token=self.api_token)
            print(f"[LLMManager] HF Inference Client re-initialized with new token.")
        else:
            # For non-HF, just update the token, client remains a placeholder
            self.client = "API_KEY_PRESENT"
            print(f"[LLMManager] API token updated for {self._protocol} client.")


    async def generate_response(self, system_prompt: str, user_prompt: str, max_new_tokens: int = 512) -> str:
        """Sends a request to the detected LLM provider."""
        if not self.api_token:
            return "Error: No API token configured. Please check your .env file."
            
        if self._protocol == "huggingface":
            return await self._call_hf(system_prompt, user_prompt, max_new_tokens)
        else:
            return await self._call_openai_compatible(system_prompt, user_prompt, max_new_tokens)

    async def _call_hf(self, system, user, tokens):
        try:
            messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
            response = ""
            for message in self.client.chat_completion(messages=messages, max_tokens=tokens, stream=True):
                response += message.choices[0].delta.content or ""
            return response.strip()
        except Exception as e:
            print(f"❌ [LLMManager] HF Error: {e}")
            return f"Error: {str(e)}"

    async def _call_openai_compatible(self, system, user, tokens):
        import httpx
        url = "https://api.groq.com/openai/v1/chat/completions" if self._protocol == "groq" else "https://api.openai.com/v1/chat/completions"
        if os.getenv("OPENAI_BASE_URL"):
            url = os.getenv("OPENAI_BASE_URL")

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_tokens": tokens
        }
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=data, timeout=30.0)
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"❌ [LLMManager] {self._protocol.upper()} Error: {e}")
            return f"Error: {str(e)}"

# Global instance
llm_manager = LLMManager()
