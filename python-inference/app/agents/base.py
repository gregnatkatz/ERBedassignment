from openai import AzureOpenAI
from abc import ABC, abstractmethod
import time
from typing import Optional
from ..config import get_settings


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, model_deployment: str):
        self.agent_id = agent_id
        self.model_deployment = model_deployment
        self.settings = get_settings()
        
        self.client = AzureOpenAI(
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=self.settings.azure_openai_endpoint
        )
        
    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,  # O3 model only supports temperature=1.0
        max_tokens: int = 2000
    ) -> str:
        """Call Azure OpenAI with the given prompts"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=max_tokens  # Use max_completion_tokens for O3/GPT-5
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM call failed for {self.agent_id}: {str(e)}")
    
    def measure_time(self, func):
        """Decorator to measure processing time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            processing_time_ms = int((time.time() - start_time) * 1000)
            if hasattr(result, 'processing_time_ms'):
                result.processing_time_ms = processing_time_ms
            return result
        return wrapper
    
    @abstractmethod
    def process(self, request):
        """Process the request and return a response"""
        pass
