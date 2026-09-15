# DeepSeek 和 Ollama 都走 OpenAI 兼容协议，只需切换 base_url 和 model
from langchain_openai import ChatOpenAI
from .config import settings

def get_llm(temperature: float = 0):
    if settings.llm_provider == "ollama":
        return ChatOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",
            model=settings.ollama_model,
            temperature=temperature,
        )
    return ChatOpenAI(
        base_url=settings.deepseek_base_url,
        api_key=settings.deepseek_api_key,
        model=settings.deepseek_model,
        temperature=temperature,
    )