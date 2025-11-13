from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_gpt5: str = "gpt-5"
    azure_openai_deployment_gpt5_chat: str = "gpt-5-chat"
    azure_openai_deployment_o3: str = "o3"
    azure_openai_deployment_o1: str = "o1"
    azure_openai_deployment_gpt41: str = "gpt-4.1"
    azure_openai_deployment_deepseek: str = "DeepSeek-V3-0324"
    azure_openai_api_version: str = "2025-01-01-preview"
    
    deepseek_endpoint: str
    deepseek_api_key: str
    deepseek_api_version: str = "2024-05-01-preview"
    
    chromadb_path: str = "./chroma_db"
    
    model_registry_path: str = "../python-training/model_registry"
    
    agl_enabled: bool = False
    
    service_port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
